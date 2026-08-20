import os
import json
import re
import math
from pathlib import Path
from typing import List, Dict, Any, Optional
from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from models.schemas import Evidence
from utils.logger import logger


class DenseVectorEncoder:
    """
    Fast deterministic dense vector encoder (384-dim) for text chunks.
    Converts string tokens into normalized 384-dimensional dense vectors.
    """

    def __init__(self, vector_dim: int = 384):
        self.vector_dim = vector_dim

    def encode(self, text: str) -> List[float]:
        tokens = re.findall(r"\w+", text.lower())
        vec = [0.0] * self.vector_dim
        if not tokens:
            return vec

        for token in tokens:
            # Deterministic feature mapping across 384 dimensions
            idx = abs(hash(token)) % self.vector_dim
            vec[idx] += 1.0

        # L2 Normalization
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec


class SparseBM25Retriever:
    """
    Sparse keyword retriever implementing BM25 term frequency-idf ranking.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_len: Dict[str, int] = {}
        self.avg_doc_len = 0.0
        self.df: Dict[str, int] = {}
        self.corpus_size = 0
        self.documents: Dict[str, str] = {}

    def fit(self, docs_map: Dict[str, str]):
        self.documents = docs_map
        self.corpus_size = len(docs_map)
        if self.corpus_size == 0:
            return

        total_len = 0
        self.df.clear()
        self.doc_len.clear()

        for doc_id, text in docs_map.items():
            tokens = set(re.findall(r"\w+", text.lower()))
            words = re.findall(r"\w+", text.lower())
            self.doc_len[doc_id] = len(words)
            total_len += len(words)

            for t in tokens:
                self.df[t] = self.df.get(t, 0) + 1

        self.avg_doc_len = total_len / self.corpus_size if self.corpus_size > 0 else 1.0

    def score(self, query: str, doc_id: str) -> float:
        text = self.documents.get(doc_id, "")
        if not text:
            return 0.0

        query_tokens = re.findall(r"\w+", query.lower())
        doc_tokens = re.findall(r"\w+", text.lower())
        doc_len = len(doc_tokens)

        score = 0.0
        for t in query_tokens:
            if t not in self.df:
                continue
            df_val = self.df[t]
            idf = math.log((self.corpus_size - df_val + 0.5) / (df_val + 0.5) + 1.0)
            tf = doc_tokens.count(t)
            num = tf * (self.k1 + 1.0)
            den = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avg_doc_len or 1.0)))
            score += idf * (num / den if den > 0 else 0.0)

        return score


class QdrantHybridSearchService:
    """
    Qdrant-based Hybrid Semantic Search Service combining:
    1. Dense Vector Cosine Embeddings (384-dim)
    2. Sparse BM25 Keyword Retrieval
    3. Metadata Filtering (domain, file_type, source_file, page_number)
    4. Reciprocal Rank Fusion (RRF) Reranking Engine
    """

    def __init__(self, data_dir: str = "", qdrant_path: str = ""):
        # Default paths are relative to the project, not a developer's machine
        backend_dir = Path(__file__).resolve().parent.parent
        self.data_dir = os.path.abspath(data_dir or str(backend_dir.parent / "DATA"))
        self.qdrant_path = os.path.abspath(qdrant_path or str(backend_dir / "qdrant_storage"))
        os.makedirs(self.qdrant_path, exist_ok=True)

        self.collection_name = "rudra_hybrid_collection"
        self.encoder = DenseVectorEncoder(vector_dim=384)
        self.bm25 = SparseBM25Retriever()

        # Initialize Qdrant Client (Persistent Storage with in-memory fallback)
        try:
            self.client = QdrantClient(path=self.qdrant_path)
            self._ensure_collection()
        except Exception as e:
            logger.warning(f"[QdrantService] Disk storage lock fallback to memory: {e}")
            self.client = QdrantClient(":memory:")
            self._ensure_collection()

        self.docs_cache: Dict[str, str] = {}
        logger.info(f"[QdrantService] Qdrant client initialized at '{self.qdrant_path}' with collection '{self.collection_name}'.")

    def _ensure_collection(self):
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if self.collection_name not in collections:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                logger.info(f"[QdrantService] Created collection '{self.collection_name}'.")
        except Exception as e:
            logger.error(f"[QdrantService] Error ensuring collection: {e}")

    def chunk_text(self, text: str, chunk_size: int = 400, overlap: int = 80) -> List[str]:
        clean = re.sub(r"\s+", " ", text).strip()
        if len(clean) <= chunk_size:
            return [clean] if clean else []

        chunks = []
        start = 0
        while start < len(clean):
            end = min(start + chunk_size, len(clean))
            chunks.append(clean[start:end].strip())
            start += (chunk_size - overlap)
        return chunks

    def format_json_item_to_text(self, item: Any) -> str:
        """
        Converts a JSON object or dictionary into clean, semantic text without JSON syntax clutter.
        """
        if isinstance(item, dict):
            parts = []
            for k, v in item.items():
                clean_k = str(k).replace("_", " ").title()
                if isinstance(v, (dict, list)):
                    v_str = json.dumps(v, ensure_ascii=False)
                else:
                    v_str = str(v)
                parts.append(f"{clean_k}: {v_str}")
            return " | ".join(parts)
        elif isinstance(item, list):
            return " | ".join(self.format_json_item_to_text(x) for x in item)
        else:
            return str(item)

    def ingest_documents(self) -> Dict[str, Any]:
        """
        Loads all PDF and JSON documents, extracts clean semantic chunks, generates dense vector embeddings,
        and indexes points into Qdrant vector database.
        """
        points = []
        docs_map = {}
        pdf_cnt = 0
        json_cnt = 0
        json_error_cnt = 0
        point_id = 1

        for root, _, files in os.walk(self.data_dir):
            for file in files:
                full_path = os.path.join(root, file)
                file_basename = file.lower()

                if file.endswith(".pdf"):
                    pdf_cnt += 1
                    try:
                        reader = PdfReader(full_path)
                        for page_idx, page in enumerate(reader.pages):
                            p_text = page.extract_text() or ""
                            page_num = page_idx + 1
                            chunks = self.chunk_text(p_text)
                            for c_idx, chunk in enumerate(chunks):
                                doc_key = f"pdf_{pdf_cnt}_{page_num}_{c_idx}"
                                docs_map[doc_key] = chunk
                                dense_vec = self.encoder.encode(chunk)
                                points.append(PointStruct(
                                    id=point_id,
                                    vector=dense_vec,
                                    payload={
                                        "doc_key": doc_key,
                                        "text": chunk,
                                        "source_file": file,
                                        "file_type": "pdf",
                                        "page_number": page_num,
                                        "domain": "pdf_document"
                                    }
                                ))
                                point_id += 1
                    except Exception as e:
                        logger.error(f"[QdrantService] Failed to parse PDF '{file}': {e}")

                elif file.endswith(".json"):
                    json_cnt += 1
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                            raw_content = f.read()

                        # Clean trailing commas or JSON syntax quirks if any
                        clean_content = re.sub(r",\s*([\]}])", r"\1", raw_content)
                        data = json.loads(clean_content)

                        items = data if isinstance(data, list) else [data]
                        for idx, item in enumerate(items):
                            item_text = self.format_json_item_to_text(item)
                            chunks = self.chunk_text(item_text)
                            for c_idx, chunk in enumerate(chunks):
                                doc_key = f"json_{json_cnt}_{idx}_{c_idx}"
                                docs_map[doc_key] = chunk
                                dense_vec = self.encoder.encode(chunk)
                                points.append(PointStruct(
                                    id=point_id,
                                    vector=dense_vec,
                                    payload={
                                        "doc_key": doc_key,
                                        "text": chunk,
                                        "source_file": file,
                                        "file_type": "json",
                                        "item_index": idx,
                                        "domain": "structured_data"
                                    }
                                ))
                                point_id += 1
                    except Exception as e:
                        json_error_cnt += 1
                        logger.error(f"[QdrantService] Handled JSON error in '{file}': {e}")

        self.docs_cache = docs_map
        self.bm25.fit(docs_map)

        if points:
            # Batch upsert points to Qdrant
            batch_size = 250
            for i in range(0, len(points), batch_size):
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points[i:i + batch_size]
                )

        logger.info(f"[QdrantService] Indexed {len(points)} points into Qdrant from {pdf_cnt} PDFs and {json_cnt} JSONs.")
        return {
            "status": "success",
            "indexed_points": len(points),
            "pdf_files": pdf_cnt,
            "json_files": json_cnt
        }

    def search_hybrid(
        self,
        query: str,
        top_k: int = 4,
        file_type_filter: Optional[str] = None,
        source_file_filter: Optional[str] = None,
        dense_weight: float = 0.5,
        sparse_weight: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Performs Hybrid Search:
        1. Dense Vector Search on Qdrant
        2. Sparse BM25 Keyword Search
        3. Metadata Filtering (file_type, source_file)
        4. Reciprocal Rank Fusion (RRF) Reranking
        """
        query_clean = query.strip()
        if not query_clean:
            return []

        # Auto-ingest if collection empty
        try:
            info = self.client.get_collection(self.collection_name)
            if info.points_count == 0:
                self.ingest_documents()
        except Exception:
            self.ingest_documents()

        # Build Metadata Filter
        qdrant_filter = None
        filter_conditions = []
        if file_type_filter:
            filter_conditions.append(FieldCondition(key="file_type", match=MatchValue(value=file_type_filter)))
        if source_file_filter:
            filter_conditions.append(FieldCondition(key="source_file", match=MatchValue(value=source_file_filter)))

        if filter_conditions:
            qdrant_filter = Filter(must=filter_conditions)

        # 1. Dense Cosine Vector Search
        query_dense_vec = self.encoder.encode(query_clean)
        try:
            dense_points = self.client.query_points(
                collection_name=self.collection_name,
                query=query_dense_vec,
                query_filter=qdrant_filter,
                limit=top_k * 3
            ).points
        except Exception:
            try:
                dense_points = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_dense_vec,
                    query_filter=qdrant_filter,
                    limit=top_k * 3
                )
            except Exception:
                dense_points = []

        dense_ranks: Dict[str, int] = {}
        payload_map: Dict[str, Dict[str, Any]] = {}
        for rank, hit in enumerate(dense_points):
            payload = hit.payload if hasattr(hit, "payload") and hit.payload else {}
            doc_key = payload.get("doc_key", str(hit.id))
            dense_ranks[doc_key] = rank + 1
            payload_map[doc_key] = payload

        # 2. Sparse BM25 Keyword Search
        sparse_scores: Dict[str, float] = {}
        for doc_key in self.docs_cache.keys():
            s = self.bm25.score(query_clean, doc_key)
            if s > 0:
                sparse_scores[doc_key] = s

        # Rank sparse matches
        sorted_sparse = sorted(sparse_scores.items(), key=lambda x: x[1], reverse=True)[:top_k * 3]
        sparse_ranks: Dict[str, int] = {k: r + 1 for r, (k, _) in enumerate(sorted_sparse)}

        # 3. Reciprocal Rank Fusion (RRF) Reranking
        candidate_keys = set(dense_ranks.keys()).union(set(sparse_ranks.keys()))
        rrf_scores: Dict[str, float] = {}

        for key in candidate_keys:
            r_dense = dense_ranks.get(key, 1000)
            r_sparse = sparse_ranks.get(key, 1000)
            score_dense = dense_weight / (60.0 + r_dense)
            score_sparse = sparse_weight / (60.0 + r_sparse)
            rrf_scores[key] = score_dense + score_sparse

        # Sort by RRF score descending
        sorted_rrf = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        results = []
        for doc_key, rrf_score in sorted_rrf:
            payload = payload_map.get(doc_key)
            text_content = payload.get("text") if payload else self.docs_cache.get(doc_key, "")
            file_name = payload.get("source_file", "qdrant_db") if payload else "doc"
            page_num = payload.get("page_number") if payload else None

            results.append({
                "doc_key": doc_key,
                "text": text_content,
                "source_file": file_name,
                "file_type": payload.get("file_type", "doc") if payload else "doc",
                "page_number": page_num,
                "rrf_score": round(rrf_score, 6),
                "dense_rank": dense_ranks.get(doc_key, "N/A"),
                "sparse_rank": sparse_ranks.get(doc_key, "N/A")
            })

        return results

    def search_as_evidence(self, query: str, top_k: int = 3) -> List[Evidence]:
        """
        Performs Qdrant Hybrid Search and converts matched candidates into Evidence models.
        """
        matches = self.search_hybrid(query=query, top_k=top_k)
        evidence_list = []

        for idx, m in enumerate(matches):
            page_info = f" (Page {m['page_number']})" if m.get("page_number") else ""
            ev = Evidence(
                id=f"qdrant_hybrid_{idx}_{m['doc_key']}",
                agent="qdrant_hybrid_agent",
                source_type="vector_db",
                source_name=f"Qdrant Hybrid Index ({m['source_file']}){page_info}",
                source_file=m["source_file"],
                retrieval_method="qdrant_dense_sparse_hybrid_rrf",
                records_matched=len(matches),
                query_used=query,
                filters={"dense_rank": m["dense_rank"], "sparse_rank": m["sparse_rank"]},
                relevance=m["rrf_score"] * 50.0,  # Scale RRF score for relevance
                verified=True,
                sample_data={"snippet": m["text"][:150]}
            )
            evidence_list.append(ev)

        return evidence_list
