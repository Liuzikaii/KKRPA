"""
Condition (if/else) node
"""
from app.engine.nodes.base import BaseNode, NodeResult
import logging

logger = logging.getLogger(__name__)


class ConditionNode(BaseNode):
    """Evaluate a condition and determine the branch."""

    NODE_TYPE = "condition"

    async def execute(self, context: dict, inputs: dict) -> NodeResult:
        condition = self.data.get("condition", "")
        logs = []

        if not condition:
            return NodeResult(success=False, error="Condition expression is required")

        logs.append(f"Evaluating condition: {condition}")

        try:
            # Build safe evaluation context
            eval_context = {
                "inputs": inputs,
                "context": context,
                "True": True,
                "False": False,
                "None": None,
                "len": len,
                "int": int,
                "float": float,
                "str": str,
                "bool": bool,
            }

            result = eval(condition, {"__builtins__": {}}, eval_context)
            branch = "true" if result else "false"
            logs.append(f"Condition result: {result} -> branch: {branch}")

            return NodeResult(
                success=True,
                output={"branch": branch, "value": bool(result)},
                logs=logs,
            )
        except Exception as e:
            return NodeResult(
                success=False,
                error=f"Condition evaluation failed: {str(e)}",
                logs=logs,
            )
