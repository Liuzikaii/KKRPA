"""
Loop node
"""
from app.engine.nodes.base import BaseNode, NodeResult
import logging

logger = logging.getLogger(__name__)


class LoopNode(BaseNode):
    """Execute a loop with configurable iterations."""

    NODE_TYPE = "loop"

    async def execute(self, context: dict, inputs: dict) -> NodeResult:
        loop_type = self.data.get("loop_type", "count")  # count, for_each
        max_iterations = self.data.get("max_iterations", 10)
        logs = []

        if loop_type == "count":
            count = self.data.get("count", 1)
            count = min(count, max_iterations)
            logs.append(f"Loop type: count, iterations: {count}")
            return NodeResult(
                success=True,
                output={
                    "loop_type": "count",
                    "iterations": count,
                    "current_index": context.get("_loop_index", 0),
                },
                logs=logs,
            )

        elif loop_type == "for_each":
            items = self.data.get("items") or inputs.get("items", [])
            if isinstance(items, str):
                items = items.split(",")
            items = items[:max_iterations]
            logs.append(f"Loop type: for_each, items count: {len(items)}")
            return NodeResult(
                success=True,
                output={
                    "loop_type": "for_each",
                    "items": items,
                    "total": len(items),
                },
                logs=logs,
            )

        return NodeResult(success=False, error=f"Unknown loop type: {loop_type}")
