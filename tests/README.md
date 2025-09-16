# Tests

This directory contains all test files for the FFS RAG project.

## Running Tests

### Using Make (Recommended)
```bash
make test
```

### Using pytest directly
```bash
pytest tests/ -v
```

### Using the test runner
```bash
python tests/run_tests.py
```

### Running individual tests
```bash
# Test reranker
python tests/test_reranker.py

# Test ingestion
python tests/test_ingestion.py
```

## Test Files

- `test_reranker.py` - Tests the CrossEncoder reranker functionality
- `test_ingestion.py` - Tests Qdrant collections and BM25 search
- `conftest.py` - Pytest configuration and fixtures
- `run_tests.py` - Simple test runner script

## Requirements

Tests require the following dependencies (installed with `pip install -e .[dev]`):
- pytest
- pytest-asyncio
- httpx
