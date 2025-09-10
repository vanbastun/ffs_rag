## Базовая Структура
rag-skeleton/
├── api/
│   └── app.py
├── configs/
│   └── config.yaml
├── rag_core/
│   ├── caching.py
│   ├── embedding.py
│   ├── generation.py
│   ├── indexing.py
│   ├── preprocessing.py
│   └── retrieval.py
├── scripts/
│   ├── index_data.py
│   └── run_eval.py
├── src/
│   └── eval/
│       ├── datasets.py
│       └── metrics.py
├── tests/
│   └── test_retrieval.py
├── data/
│   ├── raw/            # исходные документы (txt, md, json)
│   ├── processed/      # чанки и метаданные
│   └── indexes/        # faiss-индекс и словари id↔метаданные
├── .env.example
├── Makefile
├── pyproject.toml
└── README.md


Общий шаблон можно найти в tar архиве