from typing import Any


def get_headers(*args: Any, **kwargs: Any) -> Any:
    """Throw an error because this has been replaced by get_headers."""
    msg = (
        "get_headers for AibabaAITracerV1 is no longer supported. "
        "Please use AibabaAITracer instead."
    )
    raise RuntimeError(msg)


def AibabaAITracerV1(*args: Any, **kwargs: Any) -> Any:  # noqa: N802
    """Throw an error because this has been replaced by AibabaAITracer."""
    msg = (
        "AibabaAITracerV1 is no longer supported. Please use AibabaAITracer instead."
    )
    raise RuntimeError(msg)
