#!/usr/bin/env bash
set -euo pipefail

# run_in_docker.sh
# Usage: ./run_in_docker.sh [epochs] [out_dir]
# Example: ./run_in_docker.sh 20 models_docker

EPOCHS=${1:-20}
OUT_DIR=${2:-models_docker}
WORKDIR=/workspace
HOST_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Starting TensorFlow Docker container (CPU)..."
docker run --rm -it \
  -v "$HOST_DIR":$WORKDIR \
  -w $WORKDIR \
  tensorflow/tensorflow:latest \
  bash -lc "python -m pip install --upgrade pip && pip install -r requirements.txt && python -m src.train --csv data/sample_traffic.csv --out $OUT_DIR --epochs $EPOCHS --contamination 0.05"

echo "Finished. Models and outputs are in: $HOST_DIR/$OUT_DIR"
