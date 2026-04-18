"""
HTTP Request node
"""
import httpx
from app.engine.nodes.base import BaseNode, NodeResult
import logging
import json

logger = logging.getLogger(__name__)


class HttpNode(BaseNode):
    """Execute an HTTP request."""

    NODE_TYPE = "http"

    async def execute(self, context: dict, inputs: dict) -> NodeResult:
        url = self.data.get("url", "")
        method = self.data.get("method", "GET").upper()
        headers = self.data.get("headers", {})
        body = self.data.get("body", None)
        timeout = self.data.get("timeout", 30)
        logs = []

        if not url:
            return NodeResult(success=False, error="URL is required", logs=["Missing URL"])

        # Variable substitution in URL
        for key, value in inputs.items():
            url = url.replace(f"{{{{{key}}}}}", str(value))

        logs.append(f"Sending {method} request to {url}")

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if body and isinstance(body, str):
                    try:
                        body = json.loads(body)
                    except json.JSONDecodeError:
                        pass

                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=body if isinstance(body, dict) else None,
                    content=body if isinstance(body, str) else None,
                )

            logs.append(f"Response status: {response.status_code}")

            try:
                response_data = response.json()
            except Exception:
                response_data = response.text

            output = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response_data,
            }

            success = 200 <= response.status_code < 400
            if not success:
                logs.append(f"Request failed with status {response.status_code}")

            return NodeResult(success=success, output=output, logs=logs)

        except httpx.TimeoutException:
            return NodeResult(success=False, error=f"Request timed out after {timeout}s", logs=logs)
        except Exception as e:
            return NodeResult(success=False, error=str(e), logs=logs)
