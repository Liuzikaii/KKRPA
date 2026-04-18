"""
Delay / Wait node
"""
import asyncio
from app.engine.nodes.base import BaseNode, NodeResult
import logging

logger = logging.getLogger(__name__)


class DelayNode(BaseNode):
    """Wait for a specified duration before continuing."""

    NODE_TYPE = "delay"
    MAX_DELAY = 300  # 5 minutes max

    async def execute(self, context: dict, inputs: dict) -> NodeResult:
        seconds = self.data.get("seconds", 1)
        seconds = min(max(0, seconds), self.MAX_DELAY)
        logs = [f"Waiting for {seconds} seconds"]

        await asyncio.sleep(seconds)

        logs.append(f"Delay completed ({seconds}s)")
        return NodeResult(success=True, output={"waited": seconds}, logs=logs)
