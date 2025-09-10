FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml /app/
RUN pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir -e .
COPY src /app/src
CMD ["python", "-m", "src.workers.ingest"]