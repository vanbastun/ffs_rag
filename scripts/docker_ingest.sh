#!/bin/bash
# Script to run ingestion in Docker

echo "Starting Qdrant..."
docker-compose -f docker/docker-compose.yml up -d qdrant

echo "Waiting for Qdrant to be ready..."
sleep 10

echo "Running ingestion..."
docker-compose -f docker/docker-compose.yml run --rm worker

echo "Ingestion completed!"
