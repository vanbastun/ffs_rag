from time import perf_counter
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from src.api.deps import get_rag
from src.rag_core.observability import rag_errors, rag_latency, rag_requests

router = APIRouter()


class AskRequest(BaseModel):
    """Request model for RAG queries.

    Attributes:
        query: User question/query string
        k: Number of documents to retrieve (default: 6)
        filters: Optional filters for retrieval
        stream: Whether to stream response (default: True)
    """

    query: str
    k: int = 6
    filters: dict | None = None
    stream: bool = True


@router.post("/v1/ask")
def ask(req: AskRequest, rag: Any = Depends(get_rag)) -> Any:
    """Handle RAG query requests.

    Args:
        req: AskRequest containing query and parameters
        rag: RAG pipeline instance (dependency injection)

    Returns:
        Generated answer or streaming response

    Raises:
        HTTPException: On processing errors (500 status)
    """
    rag_requests.labels(method="ask").inc()
    t0 = perf_counter()
    try:
        if not req.stream:
            ans = rag.answer(req.query, k=req.k, filters=req.filters)
            return ans

        def gen() -> Any:
            """Generate streaming response chunks.

            Yields:
                Server-sent event formatted response chunks
            """
            for event in rag.answer_stream(req.query, k=req.k, filters=req.filters):
                yield f"data: {event}\n\n"

        return StreamingResponse(gen(), media_type="text/event-stream")
    except Exception as e:
        rag_errors.labels(method="ask").inc()
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        rag_latency.labels(method="ask").observe(perf_counter() - t0)
