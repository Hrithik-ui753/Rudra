from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from models.schemas import AgentResult, Evidence
from services.json_service import JSONDataService
from utils.logger import logger


class BaseAgent(ABC):
    """
    Abstract Base Class for all RUDRA Smart Campus agents.
    Defines common interface, metadata, data access, and execution contract.
    """

    def __init__(
        self,
        name: str,
        description: str,
        supported_queries: List[str],
        json_service: JSONDataService
    ):
        self.name = name
        self.description = description
        self.supported_queries = supported_queries
        self.json_service = json_service

    def is_dataset_available(self, dataset_name: str) -> bool:
        """Helper to check if a required JSON dataset exists."""
        return self.json_service.is_dataset_available(dataset_name)

    def create_evidence(
        self,
        source_type: str,
        source_name: str,
        retrieval_method: str,
        source_file: Optional[str] = None,
        records_matched: int = 0,
        filters: Optional[Dict[str, Any]] = None,
        relevance: float = 1.0,
        verified: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Evidence:
        """Helper to create a structured Evidence instance for this agent."""
        return Evidence(
            agent=self.name,
            source_type=source_type,
            source_name=source_name,
            source_file=source_file,
            retrieval_method=retrieval_method,
            records_matched=records_matched,
            filters=filters or {},
            relevance=relevance,
            verified=verified,
            metadata=metadata or {}
        )

    def data_unavailable_result(self, dataset_name: str) -> AgentResult:
        """Standard result structure when required JSON dataset is unavailable."""
        return AgentResult(
            agent_name=self.name,
            success=False,
            confidence=0.0,
            answer=f"The required dataset '{dataset_name}' is currently unavailable in the system.",
            data={"status": "data_unavailable", "dataset": dataset_name},
            error=f"Dataset '{dataset_name}' missing or empty",
            evidence=[]
        )

    @abstractmethod
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """
        Processes user query and returns a structured AgentResult.
        Must be implemented by all specialized agents.
        """
        pass
