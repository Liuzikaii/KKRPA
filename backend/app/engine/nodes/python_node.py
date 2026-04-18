"""
Python code execution node with sandbox
"""
import io
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr
from RestrictedPython import compile_restricted, safe_globals
from RestrictedPython.Guards import safe_builtins, guarded_unpack_sequence
from RestrictedPython.Eval import default_guarded_getiter, default_guarded_getattr
from app.engine.nodes.base import BaseNode, NodeResult
from app.config import settings
import signal
import logging

logger = logging.getLogger(__name__)

# Allowed modules for import in sandbox
ALLOWED_MODULES = {
    "json", "math", "re", "datetime", "time", "hashlib",
    "base64", "urllib.parse", "collections", "itertools",
    "functools", "string", "random", "decimal", "uuid",
}


def _safe_import(name, *args, **kwargs):
    """Restricted import that only allows whitelisted modules."""
    if name not in ALLOWED_MODULES:
        raise ImportError(f"Module '{name}' is not allowed in sandbox. Allowed: {', '.join(sorted(ALLOWED_MODULES))}")
    return __builtins__.__import__(name, *args, **kwargs) if isinstance(__builtins__, dict) else __import__(name, *args, **kwargs)


def _timeout_handler(signum, frame):
    raise TimeoutError("Script execution timed out")


class PythonNode(BaseNode):
    """Execute user Python code in a sandboxed environment."""

    NODE_TYPE = "python"

    async def execute(self, context: dict, inputs: dict) -> NodeResult:
        code = self.data.get("code", "")
        if not code.strip():
            return NodeResult(success=True, output=None, logs=["No code to execute"])

        timeout = self.data.get("timeout", settings.SANDBOX_TIMEOUT_SECONDS)
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        logs = []

        try:
            # Compile with RestrictedPython
            compiled = compile_restricted(code, filename="<user_script>", mode="exec")
            if compiled is None:
                return NodeResult(
                    success=False,
                    error="Failed to compile code",
                    logs=["Compilation failed - code may contain restricted syntax"],
                )

            # Build sandbox globals
            sandbox_globals = safe_globals.copy()
            sandbox_builtins = safe_builtins.copy()
            sandbox_builtins["__import__"] = _safe_import
            sandbox_builtins["_getiter_"] = default_guarded_getiter
            sandbox_builtins["_getattr_"] = default_guarded_getattr
            sandbox_builtins["_unpack_sequence_"] = guarded_unpack_sequence
            sandbox_builtins["_iter_unpack_sequence_"] = guarded_unpack_sequence

            sandbox_globals["__builtins__"] = sandbox_builtins
            sandbox_globals["print"] = lambda *args, **kwargs: stdout_capture.write(
                " ".join(str(a) for a in args) + kwargs.get("end", "\n")
            )

            # Inject inputs and context
            sandbox_globals["inputs"] = inputs
            sandbox_globals["context"] = context.copy()
            sandbox_globals["output"] = None  # User sets this for downstream nodes

            # Execute with timeout
            old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(timeout)
            try:
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    exec(compiled, sandbox_globals)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

            # Collect output
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()

            if stdout_output:
                logs.append(f"[stdout] {stdout_output.rstrip()}")
            if stderr_output:
                logs.append(f"[stderr] {stderr_output.rstrip()}")

            result_output = sandbox_globals.get("output", None)
            logs.append(f"Execution completed. Output: {result_output}")

            return NodeResult(success=True, output=result_output, logs=logs)

        except TimeoutError:
            return NodeResult(
                success=False,
                error=f"Script timed out after {timeout} seconds",
                logs=logs + [f"Timeout: {timeout}s exceeded"],
            )
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            tb = traceback.format_exc()
            logs.append(f"[error] {error_msg}")
            return NodeResult(success=False, error=error_msg, logs=logs)
