
# FFS RAG Pipeline

A production-ready RAG (Retrieval-Augmented Generation) pipeline for Fantasy Football Scout FAQ system, built with FastAPI, Qdrant, and hybrid search (dense + BM25). https://www.fantasyfootballscout.co.uk/fantasy-football-faq-and-glossary

## 🚀 Quick Start

### 1. Setup
```bash
# Install dependencies
make bootstrap

# Start infrastructure
make up

# Ingest data (from data/prepared/faq_prepared.json)
make ingest

# Test query
curl -X POST http://localhost:8000/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is prmium subscription?", "k": 5, "stream": false}'
```


### 2. Monitoring
- **API Docs**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## 🏗️ Project Structure

```
ffs_rag/
├── src/
│   ├── api/                    # FastAPI application
│   │   ├── main.py            # API entry point
│   │   ├── deps.py            # Dependency injection
│   │   └── routes/            # API endpoints
│   │       ├── health.py      # Health checks
│   │       └── query.py       # RAG query endpoint
│   ├── rag_core/              # Core RAG components
│   │   ├── __init__.py        # Main exports
│   │   ├── config.py          # Configuration management
│   │   ├── schema.py          # Pydantic data models
│   │   ├── pipeline.py        # Main RAG pipeline
│   │   ├── storage/           # Vector stores & BM25
│   │   │   ├── __init__.py
│   │   │   ├── vectorstore_qdrant.py
│   │   │   └── bm25_qdrant.py
│   │   ├── retrieval/         # Document retrieval
│   │   │   ├── __init__.py
│   │   │   ├── retriever.py   # Hybrid retriever
│   │   │   └── rerankers.py   # Cross-encoder reranker
│   │   ├── generation/        # LLM & text generation
│   │   │   ├── __init__.py
│   │   │   ├── generator.py   # LLM wrapper
│   │   │   ├── openrouter_client.py # Call to openrouter.ai API
│   │   │   └── prompting.py   # Prompt templates
│   │   ├── embeddings/        # Text embeddings
│   │   │   ├── __init__.py
│   │   │   └── embeddings.py  # FastEmbed wrapper
│   │   ├── processing/        # Text processing
│   │   │   ├── __init__.py
│   │   │   ├── chunking.py    # Text chunking
│   │   │   └── pii.py         # PII detection
│   │   └── observability/     # Monitoring & caching
│   │       ├── __init__.py
│   │       ├── observability.py # Setup Prometheus metrics
│   │       └── caching.py     # Redis caching
│   └── workers/               # Background workers
│       └── ingest.py         # Data ingestion worker
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py           # Pytest configuration
│   ├── test_ingestion.py     # Ingestion tests
│   ├── test_reranker.py      # Reranker tests
│   └── run_tests.py          # Test runner
├── scripts/                   # Utility scripts
│   ├── prepare_faq_data.py   # FAQ data preparation
│   ├── parse_faq.py          # FAQ parsing
│   ├── ingest_faq.py         # FAQ ingestion
│   └── docker_ingest.sh      # Docker ingestion script
├── data/                      # Data directory
│   ├── raw/                  # Raw data files
│   └── prepared/             # Processed data
│       └── faq_prepared.json # Structured FAQ data
├── ├── docker/                # Docker configuration
│   ├── docker-compose.yml    # Multi-service setup
│   ├── api.Dockerfile        # API container
│   ├── worker.Dockerfile     # Worker container
│   ├── grafana/              # Grafana config
│   ├── prometheus.yml        # Prometheus config
│   ├── tempo.yaml            # Tempo config
│   └── otel-collector-config.yaml # OpenTelemetry config
├── pyproject.toml            # Python dependencies
├── Makefile                  # Build commands
├── uv.lock                  # Dependency lock file
├── env_example              # Environment variables template, to be replaced to .env file after git clone.
└── README.md                 # This file
```

## 📋 Complete Pipeline Walkthrough

### Step 1: Data Preparation

The pipeline starts with FAQ data preparation:

```bash
# Parse raw FAQ text into structured format
python scripts/parse_faq.py

# Generate additional questions for better coverage
python scripts/prepare_faq_data.py
```

This creates `data/prepared/faq_prepared.json` with:
- Original questions and answers
- Generated variations for better retrieval
- Structured metadata (sections, IDs)

### Step 2: Vector Store Setup

The system uses **hybrid search** combining:

**Dense Vectors (Semantic Search):**
- Uses `jinaai/jina-embeddings-v2-small-en` model
- 512-dimensional vectors
- Cosine similarity
- Stored in Qdrant collection `documents`

**BM25 (Keyword Search):**
- Sparse vectors with IDF weighting
- Exact keyword matching
- Stored in Qdrant collection `bm25_documents`
- Multiple entries per FAQ (original + generated questions)

### Step 3: Ingestion Process

```bash
python -m src.workers.ingest
```

The ingestion process:

1. **Loads FAQ data** from `faq_prepared.json`
2. **Creates dense vectors** for each FAQ item (Q + A)
3. **Creates BM25 documents** for all questions (original + generated)
4. **Stores in Qdrant** with proper metadata
5. **Reports statistics** on created vectors/documents

### Step 4: Query Processing

When a query comes in:

1. **Embedding Generation**: Query → dense vector
2. **Hybrid Retrieval**:
   - Dense search in `documents` collection
   - BM25 search in `bm25_documents` collection
   - Score fusion with configurable alpha (default: 0.5)
3. **Reranking**: Cross-encoder reranker improves relevance
4. **Generation**: LLM generates answer from retrieved context
5. **Response**: Structured JSON response

## 🛠️ Development

### Running Tests

```bash
# Run all tests
make test

# Run specific test
python tests/test_reranker.py
python tests/test_ingestion.py

# Run with pytest directly
pytest tests/ -v
```

### Code Quality

```bash
# Lint code
make lint

# Format code
make format

# Type checking
make typecheck
```

### Docker Development

```bash
# Build and run in Docker
make up

# Run ingestion in Docker
./scripts/docker_ingest.sh

# Stop services
make down
```

## ⚙️ Configuration

### Environment Variables

```bash
# Core settings
RAG_QDRANT_URL=http://localhost:6333
RAG_REDIS_URL=redis://localhost:6379/0

# Models
RAG_EMBEDDING_MODEL=jinaai/jina-embeddings-v2-small-en
RAG_RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2

# LLM (optional)
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=deepseek/deepseek-r1-0528:free
```

## 🔧 Troubleshooting

### Common Issues

1. **Qdrant Connection Error**
   ```bash
   # Check if Qdrant is running
   curl http://localhost:6333/health

   # Restart Qdrant
   docker-compose -f docker/docker-compose.yml restart qdrant
   ```

2. **Missing Dependencies**
   ```bash
   # Reinstall dependencies
   pip install -e .
   ```

3. **Empty Collections**
   ```bash
   # Re-run ingestion
   make ingest
   ```

### Logs

```bash
# View API logs
docker-compose -f docker/docker-compose.yml logs api

# View worker logs
docker-compose -f docker/docker-compose.yml logs worker

# View all logs
docker-compose -f docker/docker-compose.yml logs -f
```
