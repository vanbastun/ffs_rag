import asyncio

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.requests import Request
from starlette.responses import Response

METRICS_PREFIX = "rag_"

rag_requests = Counter(f"{METRICS_PREFIX}requests_total", "Total RAG requests", ["method"])
rag_errors = Counter(f"{METRICS_PREFIX}errors_total", "Total RAG errors", ["method"])
rag_tokens = Counter(
    f"{METRICS_PREFIX}tokens_total", "Total tokens used", ["kind"]
)  # kind: prompt|completion
rag_cache_hits = Counter(f"{METRICS_PREFIX}cache_hits_total", "Cache hits")
rag_cache_misses = Counter(f"{METRICS_PREFIX}cache_misses_total", "Cache misses")

rag_latency = Histogram(
    f"{METRICS_PREFIX}request_latency_seconds",
    "RAG end-to-end latency",
    buckets=(0.1, 0.3, 0.6, 1.0, 2.0, 5.0),
    labelnames=["method"],
)

service_version = Gauge(f"{METRICS_PREFIX}version", "Service version", ["version"])
service_version.labels(version="1.2.3").set(1)


async def metrics_endpoint(_: Request) -> Response:
    data = await asyncio.to_thread(generate_latest)
    return Response(data, media_type=CONTENT_TYPE_LATEST)
