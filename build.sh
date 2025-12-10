#!/bin/bash
set -e

echo "Installing Git LFS..."
git lfs install

echo "Pulling LFS files..."
git lfs pull

echo "Building Docker image..."
# Build from repo root with tsp/Dockerfile
docker build -f tsp/Dockerfile -t tsp .

echo "Build complete!"

