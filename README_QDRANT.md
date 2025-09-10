# RAG Pipeline with Qdrant and FastEmbed

This project has been refactored to use Qdrant instead of PostgreSQL and FastEmbed instead of sentence-transformers.

## Quick Start

### 1. Install Dependencies

```bash
pip install -q "qdrant-client[fastembed]>=1.14.2"
# or
pip install -r requirements.txt
```

### 2. Run Qdrant

**Option A: Using Docker (Recommended)**
```bash
docker pull qdrant/qdrant
docker run -p 6333:6333 -p 6334:6334 \
   -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
   qdrant/qdrant
```

**Option B: Using the provided script**
```bash
chmod +x scripts/run_qdrant.sh
./scripts/run_qdrant.sh
```

**Option C: Using Docker Compose**
```bash
cd docker
docker-compose up qdrant
```

### 3. Ingest FAQ Data

```bash
# Run the ingest process to load FAQ data
python scripts/ingest_faq.py

# Or run the worker directly
python -m src.workers.ingest
```

### 4. Run the Application

```bash
# Start the API
cd docker
docker-compose up api

# Or run locally (after installing dependencies)
python -m src.api.main
```

## Key Changes

### Dependencies
- **Removed**: `sentence-transformers`, `psycopg`, `SQLAlchemy`
- **Added**: `qdrant-client[fastembed]`

### Vector Store
- **Old**: `PGVectorStore` using PostgreSQL with pgvector
- **New**: `QdrantVectorStore` using Qdrant

### Embeddings
- **Old**: `STEmbeddings` using sentence-transformers
- **New**: `FastEmbedEmbeddings` using FastEmbed

### Configuration
- **Old**: `database_dsn` for PostgreSQL connection
- **New**: `qdrant_url` for Qdrant connection

## Environment Variables

```bash
RAG_QDRANT_URL=http://localhost:6333
RAG_EMBEDDING_MODEL=jinaai/jina-embeddings-v2-small-en
RAG_RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
```

## FAQ Processing

The system now processes FAQ data from `data/raw/faq_ffs.txt` with the following features:

- **Section Parsing**: Automatically detects section blocks like `<Becoming a Premium Member>`
- **Q&A Extraction**: Parses questions (ending with ?) and multi-line answers
- **Structured Data**: Each FAQ item includes question, answer, and section metadata
- **Vector Search**: Questions and answers are embedded and stored for semantic search

## Benefits of the Refactor

1. **Better Performance**: Qdrant is optimized for vector operations
2. **Simpler Setup**: No need for PostgreSQL + pgvector extension
3. **Faster Embeddings**: FastEmbed is faster than sentence-transformers
4. **Better Scalability**: Qdrant handles large-scale vector operations better
5. **Modern Architecture**: More suitable for production RAG systems
6. **FAQ-Specific**: Optimized for question-answer retrieval with section context

## Web UI

Qdrant provides a web dashboard at http://localhost:6333/dashboard where you can:
- View collections and vectors
- Run queries
- Monitor performance
- Manage data
