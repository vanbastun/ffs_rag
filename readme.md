
### how to

Как стартовать
- Сгенерировать данные:
- make bootstrap
- Поднять инфраструктуру:
- make up
- Ингест:
- make ingest
- Запрос:
- curl -N -X POST localhost:8000/v1/ask -H "Content-Type: application/json" -d '{"query":"What does the password policy say?","k":6,"stream":false}'
- Метрики и дашборды:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin), дашборд RAG Overview
- Трейсы: Grafana → Explore → Tempo
Если хочешь, я подгоню конфиги под твой целевой стор (pgvector vs Chroma), добавлю полноценный BM25 (OpenSearch/ES) и подключу конкретный LLM‑провайдер под генерацию и judges.

# Базовая карта
RAG Project
├── src
│   └── eval
│       ├── datasets.py        # Загрузка, валидация, сплиты eval-наборов
│       ├── metrics.py         # Подсчёт retrieval/answer метрик
│       └── reporting.py       # Генерация отчётов и графиков
├── rag_core
│   ├── caching.py             # Кэширование эмбеддингов, поиска, ответов
│   ├── retrieval.py           # Поиск в векторном хранилище
│   ├── embedding.py           # Генерация эмбеддингов
│   ├── generation.py          # Генерация ответа LLM
│   ├── indexing.py            # Индексация документов
│   └── preprocessing.py       # Очистка и нарезка текстов
├── configs                    # YAML-конфиги пайплайна
├── scripts
│   ├── run_eval.py            # CLI для оценки качества
│   └── index_data.py          # CLI для индексации данных
└── tests                      # Автотесты

# Системная карта
| Файл | Назначение | Ключевые функции/классы | Best practices и нюансы | Ресурсы для изучения |
|------|------------|-------------------------|-------------------------|----------------------|
| **`src/eval/datasets.py`** | Управление eval‑датасетами: загрузка, валидация, сплиты, доступ к эталонным ответам и контекстам. | `load_eval`, `iter_questions`, `get_gold_context`, (опц.) `train_val_test_split`, `load_jsonl`. | JSONL/Parquet; Pydantic для схемы; фиксированные сплиты; поддержка фильтрации; воспроизводимость через seed. | [Hugging Face RAG Evaluation](https://huggingface.co/learn/cookbook/rag_evaluation) |
| **`src/eval/metrics.py`** | Подсчёт метрик качества RAG: hit rate, MRR, Recall@k, precision, faithfulness. | `compute_hit_rate`, `compute_recall`, `evaluate_generation`. | Явно отделять retrieval‑метрики от answer‑метрик; логировать подробные отчёты; указывать конфигурацию поиска. | [Evidently AI RAG metrics](https://www.evidentlyai.com/llm-guide/rag-evaluation) |
| **`src/eval/reporting.py`** | Формирование сводных отчётов о качестве (таблицы, графики, сохранение JSON с результатами). | `generate_report`, `save_report_json`, `plot_metric_trends`. | Генерацию графиков — через matplotlib/plotly; сохранять метаданные модели, конфиги поиска, timestamp. | [Matplotlib docs](https://matplotlib.org/stable/index.html) |
| **`rag_core/caching.py`** | Кэширование тяжёлых шагов пайплайна (эмбеддинги, retrieval, ответы). | `FileCache`, `get`, `set`, `clear`, (опц.) TTL, декораторы. | Разделять кэш по типам данных; TTL для динамики; измерять hit‑rate; безопасная сериализация. | [Redis caching patterns](https://redis.io/blog/10-techniques-to-improve-rag-accuracy/) |
| **`rag_core/retrieval.py`** | Логика поиска в векторном хранилище: формирование запроса, нормализация, фильтры. | `retrieve(query, top_k)`, `rerank(docs)`. | Абстракция над backend (FAISS, Milvus, Weaviate); хранить конфиг поиска; тестировать latency и recall. | [Milvus docs](https://milvus.io/docs/) |
| **`rag_core/embedding.py`** | Генерация эмбеддингов для документов и запросов. | `embed_text`, `batch_embed_texts`. | Использовать батчинг; фиксировать модель/версии; кэшировать повторяющиеся эмбеддинги; нормализовать вектор. | [OpenAI embeddings guide](https://platform.openai.com/docs/guides/embeddings) |
| **`rag_core/generation.py`** | Генерация ответа LLM с использованием найденных контекстов. | `generate_answer(question, context)`. | Контролировать длину и релевантность ответа; логировать промпты; параметризировать temperature/top_p. | [LangChain RAG Chains](https://python.langchain.com/docs/use_cases/question_answering/) |
| **`rag_core/indexing.py`** | Подготовка и индексация документов в векторную БД. | `index_documents`, `delete_document`, `update_document`. | Предварительная очистка текста; хранение doc_id/chunk_id; idempotent‑загрузка. | [Pinecone indexing guide](https://docs.pinecone.io/docs/indexes) |
| **`rag_core/preprocessing.py`** | Очистка и нарезка текстов на чанки перед индексированием. | `split_into_chunks`, `normalize_text`. | Оптимальный размер чанка для retrieval; удалять лишние символы; сохранять привязку к исходнику. | [LangChain text splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters/) |
| **`configs/*.yaml`** | Конфигурация пайплайна (путь к данным, модель, параметры поиска, размеры чанков). | — | Версионировать конфиги; валидировать при загрузке; хранить рядом с результатами eval. | [Hydra config management](https://hydra.cc/) |
| **`scripts/run_eval.py`** | CLI для прогона оценки качества. | `main()` с загрузкой датасета, пайплайна, подсчётом метрик и выводом отчёта. | Логировать шаги; принимать аргументы CLI; сохранять отчёт с timestamp. | [Click CLI](https://click.palletsprojects.com/) |
| **`scripts/index_data.py`** | CLI для первичной индексации данных в векторное хранилище. | `main()` с загрузкой источников, нарезкой и записью в БД. | Логировать статистику; проверять наличие дубликатов; хэшировать содержимое. | [FAISS docs](https://faiss.ai/) |
| **`tests/*`** | Набор автотестов для всех ключевых модулей. | Тесты с pytest, фикстуры для моков. | Покрывать тестами метрики, кэш, retrieval; использовать testcontainers для сервисов. | [pytest docs](https://docs.pytest.org/) |

