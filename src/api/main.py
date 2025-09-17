from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from src.api.deps import get_rag
from src.api.routes import health, query
from src.rag_core.observability import metrics_endpoint


def _init_tracing() -> None:
    """Initialize OpenTelemetry tracing for the RAG API.

    Sets up OTLP HTTP exporter and batch span processor for distributed tracing.
    """
    provider = TracerProvider(resource=Resource.create({"service.name": "rag-api"}))
    exporter = OTLPSpanExporter()
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)


app = FastAPI(title="RAG API", version="0.1.0")
_init_tracing()


@app.on_event("startup")
async def startup_event() -> None:
    """Pre-warm models during application startup to avoid download delays on first API call."""
    print("🚀 Starting RAG API...")
    print("📥 Pre-warming models (this may take a moment on first run)...")

    try:
        # Pre-warm the RAG pipeline (downloads and loads models)
        get_rag()
        print("✅ Models pre-warmed successfully!")
        print("🎯 API ready to serve requests")
    except Exception as e:
        print(f"❌ Error pre-warming models: {e}")
        # Don't fail startup - models will be loaded on first request
        print("⚠️  Models will be loaded on first request")


app.include_router(health.router)
app.include_router(query.router)

app.add_api_route("/metrics", metrics_endpoint, methods=["GET"])
