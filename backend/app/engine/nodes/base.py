"""
Base node abstraction for workflow execution
"""
from abc import ABC, abstractmethod
from typing import Any, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class NodeResult:
    """Result of a node execution."""
    success: bool
    output: Any = None
    error: Optional[str] = None
    logs: list[str] = field(default_factory=list)


class BaseNode(ABC):
    """Abstract base class for all workflow nodes."""

    NODE_TYPE: str = "base"

    def __init__(self, node_id: str, node_data: dict):
        self.node_id = node_id
        self.data = node_data
        self.label = node_data.get("label", "Unnamed Node")

    @abstractmethod
    async def execute(self, context: dict, inputs: dict) -> NodeResult:
        """
        Execute this node.

        Args:
            context: Shared execution context with variables
            inputs: Data from connected upstream nodes

        Returns:
            NodeResult with success status and output
        """
        pass

    def __repr__(self):
        return f"<{self.NODE_TYPE}Node:{self.node_id} '{self.label}'>"
