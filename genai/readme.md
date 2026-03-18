# GenAI Texture Pipeline


![GenAI - Pipeline](../docs/architecture/genai/pipeline.svg)

GenAI uses a split architecture:
- **Client (local)**: `main.ipynb` calls `generate_texture` from `genai/client.py`.
- **Server (remote)**: `genai/server.py` hosts the Flask API and runs generation via `genai/models.py` + `MV-Adapter`.


## 1) Credentials Setup (global)

**Configure environment variables**
   ```bash
   cp genai/.env.example .env
   ```
   Then fill `.env` with your values:
   - `MV_ADAPTER_PATH`
   - `SSH_HOST`
   - `SSH_USER`
   - `SSH_KEY_PATH`
   - `HF_TOKEN`

## 2) Server setup (Disco.hevs.ch)


1. **Clone the repository**
    - Clone the repository by doing 
    ```
    git clone git@github.com:Toys-R-Us-Rex/Duckify.git
    ```

2. **Prepare environment**
   - Go to project root on the cluster (/Duckify).
   - Activate your uv env by doing 
   ```
   uv sync
   ```

3. **Start API server**
   ```bash
   uv run genai/server.py
   ```
   Use `screen` if needed to maintain the api open while leaving the connection.

## 3) Client setup (local machine)

1. **Install dependencies**
   ```bash
   uv sync
   ```

## 3) Run from `main.ipynb`

```python

#example
import os
from genai.client import generate_texture

input_mesh = "3dmodel/duck/duck_model_3.obj"
output_directory = "output/"

prompt = "A cartoon styled batman duck with a batman logo on the side"
negative_prompt = "realistic, ugly, deformed, blurry, bad anatomy"
prompt_wrapper = None # prompt that complete the initial prompt

mesh_path, extracted_files = generate_texture(
    fichier_obj=input_mesh,
    prompt=prompt,
    output_dir=output_directory,
    negative_prompt=negative_prompt,
    prompt_wrapper=prompt_wrapper,
    steps=30,
    guidance=6.0,
)

print(f"Files: {extracted_files}")
```
