#!/bin/bash

# Simple script to run Qdrant locally
# This creates a local Qdrant instance for development

echo "Starting Qdrant locally..."

# Create storage directory if it doesn't exist
mkdir -p qdrant_storage

# Run Qdrant with Docker
docker run -p 6333:6333 -p 6334:6334 \
   -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
   qdrant/qdrant

echo "Qdrant is running on http://localhost:6333"
echo "Web UI available at http://localhost:6333/dashboard"
