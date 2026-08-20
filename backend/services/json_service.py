import json
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from utils.logger import logger


class JSONDataService:
    """
    Service for discovering, loading, caching, and querying JSON datasets.
    Ensures zero mutation to source JSON files and graceful failure handling.
    """

    def __init__(self, data_dir: Union[str, Path]):
        self.data_dir = Path(data_dir).resolve()
        self._cache: Dict[str, Any] = {}
        self._file_registry: Dict[str, Path] = {}
        self.discover_and_preload()

    def discover_and_preload(self) -> None:
        """Recursively scan data directory for JSON files and load them into memory cache."""
        if not self.data_dir.exists():
            logger.warning(f"Data directory '{self.data_dir}' does not exist.")
            return

        logger.info(f"Scanning data directory: '{self.data_dir}'")
        for json_path in self.data_dir.rglob("*.json"):
            try:
                rel_path = json_path.relative_to(self.data_dir)
                norm_key = str(rel_path.with_suffix("")).replace("\\", "/").lower()
                basename_key = json_path.stem.lower()

                self._file_registry[norm_key] = json_path
                self._file_registry[basename_key] = json_path

                content = self._safe_load_file(json_path)
                if content is not None:
                    self._cache[norm_key] = content
                    self._cache[basename_key] = content
                    logger.info(f"Loaded JSON dataset '{norm_key}' ({json_path.name})")
            except Exception as e:
                logger.error(f"Failed to process file '{json_path}': {e}")

        logger.info(f"Preloaded {len(self._cache)} JSON dataset keys into memory.")

    def _safe_load_file(self, file_path: Path) -> Optional[Any]:
        """Safely open and read a JSON file without modifying it."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON file '{file_path}': {e}")
            return None

    def get_dataset(self, dataset_name: str) -> Optional[Any]:
        """
        Retrieves a cached JSON dataset by key or filename stem.
        Returns None if dataset is missing or unavailable.
        """
        key = dataset_name.lower().replace("\\", "/").removesuffix(".json")
        return self._cache.get(key)

    def _clean_term(self, text: str) -> str:
        """Strips trailing punctuation from search terms."""
        return re.sub(r"[^\w\s\-]", "", text).strip().lower()

    def search_in_dataset(
        self,
        dataset_name: str,
        query: str,
        fields: Optional[List[str]] = None
    ) -> List[Any]:
        """
        Search for matching items inside a specified JSON dataset.
        Handles list of dicts, list of lists, and nested dictionary structures safely.
        """
        data = self.get_dataset(dataset_name)
        if not data:
            return []

        # Extract roll number pattern if present (e.g. 1602-24-737-016)
        roll_match = re.search(r"1602[-\s]?\d{2}[-\s]?\d{3}[-\s]?\d{3}", query, re.IGNORECASE)
        target_roll = roll_match.group(0).replace(" ", "-").lower() if roll_match else None

        # Clean query terms
        words = query.lower().split()
        query_terms = [self._clean_term(w) for w in words if len(self._clean_term(w)) > 1]

        if target_roll:
            query_terms.append(target_roll)

        if not query_terms:
            return []

        results = []

        if isinstance(data, list):
            for item in data:
                match_found = False
                if isinstance(item, dict):
                    searchable_str = " ".join(
                        str(v).lower() for k, v in item.items() 
                        if not fields or k in fields
                    )
                    if target_roll and target_roll in searchable_str:
                        match_found = True
                    elif any(term in searchable_str for term in query_terms if term not in ["tell", "about", "what", "is", "the", "for", "show"]):
                        match_found = True

                elif isinstance(item, list):
                    searchable_str = " ".join(str(v).lower() for v in item)
                    if target_roll and target_roll in searchable_str:
                        match_found = True
                    elif any(term in searchable_str for term in query_terms if term not in ["tell", "about", "what", "is", "the", "for", "show"]):
                        match_found = True
                
                if match_found:
                    results.append(item)

        elif isinstance(data, dict):
            for k, v in data.items():
                if target_roll and (target_roll in k.lower() or target_roll in str(v).lower()):
                    results.append({"key": k, "value": v})
                elif any(term in k.lower() or term in str(v).lower() for term in query_terms if term not in ["tell", "about", "what"]):
                    results.append({"key": k, "value": v})

        return results

    def is_dataset_available(self, dataset_name: str) -> bool:
        """Check if a dataset key exists and is non-empty."""
        key = dataset_name.lower().replace("\\", "/").removesuffix(".json")
        return key in self._cache and self._cache[key] is not None
