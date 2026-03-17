#!/bin/bash
#SBATCH --job-name=Duckify_GridSearch
#SBATCH --output=logs/job_%j.out
#SBATCH --error=logs/job_%j.err
#SBATCH --gres=gpu:1
#SBATCH --mem=80G
#SBATCH --time=01:00:00

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

cd /home/kevin.voisin/Duckify/genai/MV-Adapter/ # Change to the directory where the script is located
mkdir -p "$MV_OUTPUT_DIR"

echo "Lancement de MV-Adapter..."

python -m scripts.texture_t2tex \
    --mesh "$MV_MESH_PATH" \
    --text "$MV_PROMPT" \
    --save_dir "$MV_OUTPUT_DIR" \
    --save_name "$MV_SAVE_NAME" \
    --num_inference_steps "$MV_STEPS" \
    --guidance_scale "$MV_GUIDANCE"

