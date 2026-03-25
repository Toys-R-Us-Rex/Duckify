#!/bin/bash
#SBATCH --job-name=Duckify_TextureGen
#SBATCH --output=logs/job_%j.out
#SBATCH --error=logs/job_%j.err
#SBATCH --gres=gpu:1
#SBATCH --mem=80G
#SBATCH --time=00:30:00

set -euo pipefail

cd "$MV_ADAPTER_PATH"

echo "Starting MV-Adapter job in Docker container '$MV_DOCKER_CONTAINER_NAME'..."

docker exec \
  -e HF_TOKEN="${HF_TOKEN:-}" \
  "$MV_DOCKER_CONTAINER_NAME" \
  python -m scripts.texture_t2tex \
  --mesh "$MV_MESH_PATH" \
  --text "$MV_PROMPT" \
  --save_dir "$MV_OUTPUT_DIR" \
  --save_name "$MV_SAVE_NAME" \
  --num_inference_steps "$MV_STEPS" \
  --guidance_scale "$MV_GUIDANCE" \
  --negative_text "$MV_NEGATIVE_PROMPT"

echo "MV-Adapter job finished."
