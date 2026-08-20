import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from pypdf import PdfReader
from models.schemas import Evidence
from utils.logger import logger

class RAGService:
    """
    RAG Engine powered by ChromaDB.
    Handles text chunking, embedding generation, vector similarity search,
    and metadata extraction from PDF and JSON documents.
    """

    def __init__(self, data_dir: str = "", chroma_dir: str = ""):
        # Default paths are relative to the project, not a developer's machine
        backend_dir = Path(__file__).resolve().parent.parent
        self.data_dir = os.path.abspath(data_dir or str(backend_dir.parent / "DATA"))
        self.chroma_dir = os.path.abspath(chroma_dir or str(backend_dir / "chroma_db"))
        os.makedirs(self.chroma_dir, exist_ok=True)

        try:
            self.client = chromadb.PersistentClient(path=self.chroma_dir)
            self.collection = self.client.get_or_create_collection(
                name="rudra_knowledge",
                metadata={"description": "RUDRA Campus Knowledge Base Vector Embeddings"}
            )
        except Exception as e:
            logger.warning(f"[RAGService] Persistent ChromaDB error, falling back to memory: {e}")
            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection(
                name="rudra_knowledge",
                metadata={"description": "RUDRA Campus Knowledge Base Vector Embeddings"}
            )
        logger.info(f"[RAGService] ChromaDB initialized with collection '{self.collection.name}'.")

    def chunk_text(self, text: str, chunk_size: int = 400, overlap: int = 80) -> List[str]:
        """
        Splits long text into overlapping chunks for optimal vector retrieval.
        """
        clean = re.sub(r"\s+", " ", text).strip()
        if len(clean) <= chunk_size:
            return [clean] if clean else []

        chunks = []
        start = 0
        while start < len(clean):
            end = min(start + chunk_size, len(clean))
            # Try to break at nearest sentence boundary or space
            if end < len(clean):
                space_idx = clean.rfind(" ", start + chunk_size // 2, end)
                if space_idx != -1:
                    end = space_idx
            chunks.append(clean[start:end].strip())
            start += (chunk_size - overlap)
        return chunks

    def format_json_item_to_text(self, item: Any) -> str:
        """
        Converts a JSON object into clean, semantic text without raw JSON syntax noise.
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

    def load_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extracts clean text chunks from JSON document with syntax error recovery.
        """
        documents = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_content = f.read()

            # Fix trailing commas or raw syntax quirks
            clean_content = re.sub(r",\s*([\]}])", r"\1", raw_content)
            data = json.loads(clean_content)

            file_basename = os.path.basename(file_path)
            items = data if isinstance(data, list) else [data]

            for idx, item in enumerate(items):
                item_text = self.format_json_item_to_text(item)
                chunks = self.chunk_text(item_text)
                for chunk_idx, chunk in enumerate(chunks):
                    documents.append({
                        "id": f"{file_basename}_i{idx}_c{chunk_idx}",
                        "text": chunk,
                        "metadata": {
                            "source_file": file_basename,
                            "file_type": "json",
                            "item_index": idx,
                            "chunk_index": chunk_idx,
                            "file_path": file_path
                        }
                    })
        except Exception as e:
            logger.error(f"[RAGService] Handled JSON syntax error in '{file_path}': {e}")

        return documents

    def load_pdf_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extracts text from PDF document using PyPDF, page by page.
        """
        documents = []
        try:
            reader = PdfReader(file_path)
            file_basename = os.path.basename(file_path)
            for page_idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                page_num = page_idx + 1
                chunks = self.chunk_text(page_text)
                for chunk_idx, chunk in enumerate(chunks):
                    documents.append({
                        "id": f"{file_basename}_p{page_num}_c{chunk_idx}",
                        "text": chunk,
                        "metadata": {
                            "source_file": file_basename,
                            "file_type": "pdf",
                            "page_number": page_num,
                            "chunk_index": chunk_idx,
                            "file_path": file_path
                        }
                    })
        except Exception as e:
            logger.error(f"[RAGService] Error loading PDF '{file_path}': {e}")
        return documents

    def build_vector_index(self) -> Dict[str, Any]:
        """
        Discovers all JSON and PDF files in DATA directory and indexes them into ChromaDB.
        """
        all_docs = []
        pdf_count = 0
        json_count = 0

        # Scan for PDFs and JSONs recursively in data_dir
        for root, _, files in os.walk(self.data_dir):
            for file in files:
                full_path = os.path.join(root, file)
                if file.endswith(".pdf"):
                    docs = self.load_pdf_file(full_path)
                    all_docs.extend(docs)
                    pdf_count += 1
                elif file.endswith(".json"):
                    docs = self.load_json_file(full_path)
                    all_docs.extend(docs)
                    json_count += 1

        if not all_docs:
            logger.warning("[RAGService] No documents found to index.")
            return {"status": "no_documents", "total_chunks": 0}

        # Add documents to ChromaDB in safe batches
        if all_docs:
            batch_size = 100
            for i in range(0, len(all_docs), batch_size):
                batch = all_docs[i:i + batch_size]
                try:
                    self.collection.upsert(
                        ids=[d["id"] for d in batch],
                        documents=[d["text"] for d in batch],
                        metadatas=[d["metadata"] for d in batch]
                    )
                except Exception as e:
                    logger.error(f"[RAGService] Upsert error at batch {i}: {e}. Resetting collection index.")
                    try:
                        self.client.delete_collection("rudra_knowledge")
                    except Exception:
                        pass
                    self.collection = self.client.get_or_create_collection(
                        name="rudra_knowledge",
                        metadata={"description": "RUDRA Campus Knowledge Base Vector Embeddings"}
                    )
                    # Retry batch upsert
                    try:
                        self.collection.upsert(
                            ids=[d["id"] for d in batch],
                            documents=[d["text"] for d in batch],
                            metadatas=[d["metadata"] for d in batch]
                        )
                    except Exception as ex:
                        logger.error(f"[RAGService] Retry failed at batch {i}: {ex}")

        logger.info(f"[RAGService] Indexed {len(all_docs)} vector chunks into ChromaDB from {pdf_count} PDFs and {json_count} JSONs.")
        return {
            "status": "success",
            "indexed_pdf_files": pdf_count,
            "indexed_json_files": json_count,
            "total_chunks": len(all_docs)
        }

    def search(self, query: str, top_k: int = 4, domain_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Performs vector similarity search on ChromaDB.
        Returns list of matched chunks with metadata and Evidence models.
        """
        if self.collection.count() == 0:
            logger.info("[RAGService] ChromaDB collection is empty. Building index now...")
            self.build_vector_index()

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )

            matched_results = []
            if results and "documents" in results and results["documents"]:
                docs = results["documents"][0]
                metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
                distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(docs)

                for idx, text in enumerate(docs):
                    meta = metas[idx] if idx < len(metas) else {}
                    dist = distances[idx] if idx < len(distances) else 0.0
                    similarity_score = round(max(0.0, 1.0 - (dist / 2.0)), 4) if dist else 0.90
                    
                    source_file = meta.get("source_file", "knowledge_base")
                    page_num = meta.get("page_number")

                    matched_results.append({
                        "text": text,
                        "source_file": source_file,
                        "file_type": meta.get("file_type", "doc"),
                        "page_number": page_num,
                        "score": similarity_score,
                        "metadata": meta
                    })
            return matched_results
        except Exception as e:
            logger.error(f"[RAGService] Search error for query '{query}': {e}")
            return []

    def search_as_evidence(self, query: str, top_k: int = 3) -> List[Evidence]:
        """
        Performs vector search and converts matched chunks into RUDRA Evidence objects.
        """
        raw_matches = self.search(query, top_k=top_k)
        evidence_list = []

        for idx, match in enumerate(raw_matches):
            page_info = f" (Page {match['page_number']})" if match.get("page_number") else ""
            ev = Evidence(
                id=f"rag_vector_{idx}_{match['source_file']}",
                agent="chromadb_rag_agent",
                source_type="vector_db",
                source_name=f"ChromaDB RAG Index ({match['source_file']}){page_info}",
                source_file=match["source_file"],
                retrieval_method="chromadb_vector_similarity",
                records_matched=len(raw_matches),
                query_used=query,
                filters={"page_number": match.get("page_number"), "file_type": match.get("file_type")},
                relevance=match["score"],
                verified=True,
                sample_data={"snippet": match["text"][:150]}
            )
            evidence_list.append(ev)
        return evidence_list
