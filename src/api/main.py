from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from src.api.routes import health, query
from src.rag_core.observability import metrics_endpoint


def _init_tracing():
    """Initialize OpenTelemetry tracing for the RAG API.
    
    Sets up OTLP HTTP exporter and batch span processor for distributed tracing.
    """
    provider = TracerProvider(resource=Resource.create({"service.name": "rag-api"}))
    exporter = OTLPSpanExporter()
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)


app = FastAPI(title="RAG API", version="0.1.0")
_init_tracing()

app.include_router(health.router)
app.include_router(query.router)

app.add_api_route("/metrics", metrics_endpoint, methods=["GET"])
