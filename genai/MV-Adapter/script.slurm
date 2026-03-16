#!/bin/bash
#SBATCH --job-name=Duckify_GridSearch
#SBATCH --output=logs/job_%j.out
#SBATCH --error=logs/job_%j.err
#SBATCH --gres=gpu:1
#SBATCH --mem=80G
#SBATCH --time=05:00:00  # Temps augmenté pour 105 générations

echo "--- Démarrage de l'environnement ---"

source ~/miniconda3/etc/profile.d/conda.sh || source ~/anaconda3/etc/profile.d/conda.sh
conda activate mvadapter

export CC=$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-gcc
export CXX=$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-g++
export CUDA_HOME=$CONDA_PREFIX
export PATH=$CUDA_HOME/bin:$PATH
export CPATH=$CONDA_PREFIX/include:$CPATH
export CUDA_VISIBLE_DEVICES=1
export LIBRARY_PATH=$CONDA_PREFIX/lib:$LIBRARY_PATH
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
export PYTORCH_CUDA_LIB=$CONDA_PREFIX/lib/python3.10/site-packages/nvidia/cuda_runtime/lib
export HF_TOKEN="hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" # Your Hugging Face token here

MESH_PATH="3d_models/official_model_1.glb"
OUTPUT_DIR="outputs/model_output_$(date '+%Y-%m-%d-%H-%M-%S')"

NEG_PROMPT="realistic, gradients, 3D shading, glossy,shiny, background, complex patterns, thin lines, messy, yellow, purple, orange, pink, gray, brown, ugly, deformed, blurry, bad anatomy"

PROMPT="A cartoon styled batman duck with a batman logo on the side"

cd /home/kevin.voisin/MV-Adapter/ # Change to the directory where your MV-adapter folder is located
mkdir -p logs
mkdir -p "$OUTPUT_DIR"

echo "--- Démarrage ---"
SAVE_NAME="duckify_$(date '+%Y-%m-%d-%H-%M-%S')"

python -m scripts.texture_t2tex \
            --mesh "$MESH_PATH" \
            --text "$PROMPT" \
            --negative_text "$NEG_PROMPT" \
            --save_dir "$OUTPUT_DIR" \
            --save_name "$SAVE_NAME" \
            --num_inference_steps "30.0" \
            --guidance_scale "6.0"

echo "--- Processus terminé ---"
