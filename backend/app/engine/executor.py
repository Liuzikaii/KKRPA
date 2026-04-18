"""
Workflow Execution Engine
Parses React Flow graph data and executes nodes in topological order.
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional
from collections import defaultdict, deque
from app.engine.nodes.base import BaseNode, NodeResult
from app.engine.nodes.python_node import PythonNode
from app.engine.nodes.http_node import HttpNode
from app.engine.nodes.condition_node import ConditionNode
from app.engine.nodes.loop_node import LoopNode
from app.engine.nodes.delay_node import DelayNode

logger = logging.getLogger(__name__)

# Node type registry
NODE_REGISTRY: dict[str, type[BaseNode]] = {
    "python": PythonNode,
    "http": HttpNode,
    "condition": ConditionNode,
    "loop": LoopNode,
    "delay": DelayNode,
    "start": None,  # Virtual nodes
    "end": None,
}


class ExecutionContext:
    """Shared context across the workflow execution."""

    def __init__(self):
        self.variables: dict = {}
        self.node_outputs: dict[str, any] = {}
        self.logs: list[str] = []
        self.started_at: datetime = datetime.utcnow()
        self.finished_at: Optional[datetime] = None
        self.is_cancelled: bool = False

    def add_log(self, message: str):
        timestamp = datetime.utcnow().strftime("%H:%M:%S.%f")[:-3]
        entry = f"[{timestamp}] {message}"
        self.logs.append(entry)
        logger.info(entry)

    def get_all_logs(self) -> str:
        return "\n".join(self.logs)


class WorkflowExecutor:
    """
    Main workflow executor.
    Parses React Flow graph JSON and executes nodes in order.
    """

    def __init__(self, graph_data: dict):
        self.nodes_data = graph_data.get("nodes", [])
        self.edges_data = graph_data.get("edges", [])
        self.context = ExecutionContext()

    def _build_adjacency(self) -> tuple[dict, dict]:
        """Build adjacency list and in-degree map from edges."""
        adj = defaultdict(list)
        in_degree = defaultdict(int)

        # Initialize all nodes
        for node in self.nodes_data:
            node_id = node["id"]
            if node_id not in in_degree:
                in_degree[node_id] = 0

        for edge in self.edges_data:
            source = edge["source"]
            target = edge["target"]
            source_handle = edge.get("sourceHandle", "default")
            adj[source].append({"target": target, "handle": source_handle})
            in_degree[target] = in_degree.get(target, 0) + 1

        return adj, in_degree

    def _topological_sort(self) -> list[str]:
        """Topological sort for execution order."""
        adj, in_degree = self._build_adjacency()
        queue = deque()

        for node_id, degree in in_degree.items():
            if degree == 0:
                queue.append(node_id)

        order = []
        while queue:
            node_id = queue.popleft()
            order.append(node_id)
            for edge_info in adj[node_id]:
                target = edge_info["target"]
                in_degree[target] -= 1
                if in_degree[target] == 0:
                    queue.append(target)

        if len(order) != len(in_degree):
            raise ValueError("Workflow contains a cycle - cannot execute")

        return order

    def _create_node(self, node_data: dict) -> Optional[BaseNode]:
        """Create a node instance from graph data."""
        node_type = node_data.get("type", "").lower()
        node_id = node_data["id"]
        data = node_data.get("data", {})

        if node_type in ("start", "end"):
            return None

        node_class = NODE_REGISTRY.get(node_type)
        if node_class is None:
            logger.warning(f"Unknown node type: {node_type}, skipping {node_id}")
            return None

        return node_class(node_id=node_id, node_data=data)

    def _get_inputs_for_node(self, node_id: str) -> dict:
        """Collect outputs from upstream nodes as inputs."""
        inputs = {}
        for edge in self.edges_data:
            if edge["target"] == node_id:
                source_id = edge["source"]
                if source_id in self.context.node_outputs:
                    handle = edge.get("sourceHandle", "default")
                    inputs[f"{source_id}_{handle}"] = self.context.node_outputs[source_id]
                    inputs["_latest"] = self.context.node_outputs[source_id]
        return inputs

    def _should_skip_node(self, node_id: str) -> bool:
        """Check if node should be skipped due to condition branching."""
        for edge in self.edges_data:
            if edge["target"] == node_id:
                source_id = edge["source"]
                source_handle = edge.get("sourceHandle", "default")
                output = self.context.node_outputs.get(source_id)

                # If upstream is a condition node, check the branch
                if output and isinstance(output, dict) and "branch" in output:
                    if source_handle != output["branch"]:
                        return True
        return False

    async def execute(self) -> dict:
        """Execute the entire workflow."""
        self.context.add_log("=== Workflow execution started ===")
        results = {}
        errors = []

        try:
            execution_order = self._topological_sort()
            self.context.add_log(f"Execution order: {len(execution_order)} nodes")

            # Build node map
            node_map = {n["id"]: n for n in self.nodes_data}

            for node_id in execution_order:
                if self.context.is_cancelled:
                    self.context.add_log("Execution cancelled by user")
                    break

                node_data = node_map.get(node_id)
                if not node_data:
                    continue

                # Skip based on condition branches
                if self._should_skip_node(node_id):
                    self.context.add_log(f"Skipping node [{node_id}] due to condition branch")
                    continue

                node = self._create_node(node_data)
                if node is None:
                    self.context.add_log(f"Node [{node_id}] ({node_data.get('type', 'unknown')}) - pass-through")
                    continue

                self.context.add_log(f"Executing node [{node.label}] (type: {node.NODE_TYPE})")

                # Gather inputs
                inputs = self._get_inputs_for_node(node_id)

                # Execute
                result = await node.execute(self.context.variables, inputs)
                results[node_id] = result

                # Store output for downstream nodes
                self.context.node_outputs[node_id] = result.output

                # Log results
                for log_line in result.logs:
                    self.context.add_log(f"  [{node.label}] {log_line}")

                if not result.success:
                    error_msg = f"Node [{node.label}] failed: {result.error}"
                    self.context.add_log(f"ERROR: {error_msg}")
                    errors.append(error_msg)
                    break  # Stop on error

            self.context.finished_at = datetime.utcnow()
            duration = (self.context.finished_at - self.context.started_at).total_seconds()
            success = len(errors) == 0

            self.context.add_log(f"=== Workflow {'completed' if success else 'failed'} in {duration:.2f}s ===")

            return {
                "success": success,
                "results": {k: {"output": v.output, "success": v.success} for k, v in results.items()},
                "errors": errors,
                "logs": self.context.get_all_logs(),
                "duration": duration,
            }

        except Exception as e:
            self.context.add_log(f"FATAL ERROR: {str(e)}")
            return {
                "success": False,
                "results": {},
                "errors": [str(e)],
                "logs": self.context.get_all_logs(),
                "duration": 0,
            }
