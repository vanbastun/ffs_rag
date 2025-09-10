from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from src.api.deps import get_rag
from src.rag_core.observability import rag_errors, rag_latency, rag_requests

router = APIRouter()


class AskRequest(BaseModel):
    query: str
    k: int = 6
    filters: dict | None = None
    stream: bool = True


@router.post("/v1/ask")
def ask(req: AskRequest, rag=Depends(get_rag)):
    rag_requests.inc()
    t0 = perf_counter()
    try:
        if not req.stream:
            ans = rag.answer(req.query, k=req.k, filters=req.filters)
            return ans

        def gen():
            for event in rag.answer_stream(req.query, k=req.k, filters=req.filters):
                yield f"data: {event}\n\n"

        return StreamingResponse(gen(), media_type="text/event-stream")
    except Exception as e:
        rag_errors.inc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        rag_latency.observe(perf_counter() - t0)
