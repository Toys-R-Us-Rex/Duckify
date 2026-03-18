# AI Texture Generation Pipeline

![GenAI - Pipeline](../docs/architecture/genai/pipeline.svg)

GenAI uses a split architecture:
- **Client (local)**: the `generate_texture` function from `genai/client.py` sends the model, prompt and parameters to the server.
- **Server (remote)**: `genai/server.py` hosts the Flask API and runs generation via `genai/models.py` + `MV-Adapter`.

## Installation

### Credentials Setup (client & server)

1. Copy the appropriate ENV file
   ```bash
   # On the server
   cp .env.server.example .env

   # On the client
   cp .env.client.example .env
   ```

2. Fill in the appropriate variables
   |Variable|Description|Where|
   |:---|:---|:---|
   |MV_ADAPTER_PATH|Path to the directory where MV-Adapter is installed|Server|
   |SSH_HOST|Host address of the server|Client|
   |SSH_USER|SSH user on the server|Client|
   |SSH_KEY_PATH|Path to the SSH key to use|Client|
   |HF_TOKEN|Huggingface token|Client|

### Server setup (disco.hevs.ch)

1. Clone the main repository
   ```bash
   git clone git@github.com:Toys-R-Us-Rex/Duckify.git
   ```

2. Clone MV-Adapter
   ```bash
   git clone git@github.com:Toys-R-Us-Rex/MV-Adapter.git
   ```

3. Go in the GenAI directory
   ```bash
   cd Duckify/genai
   ```

4. Set up environment variables (see [Credentials Setup](#credentials-setup-client--server))

5. Download all dependencies
   ```bash
   uv sync
   ```

### Client setup (local machine)

1. Clone the main repository
   ```bash
   git clone git@github.com:Toys-R-Us-Rex/Duckify.git
   ```

2. Go in the GenAI directory
   ```bash
   cd Duckify/genai
   ```

3. Set up environment variables (see [Credentials Setup](#credentials-setup-client--server))

4. Install all dependencies
   ```bash
   uv sync
   ```

## Usage

### On the server

1. Start the API server
   ```bash
   uv run server.py
   ```

   > [!TIP]
   > Use `screen` or `tmux` to keep the server running while closing you connection with the server

### On the client

1. From [`main.ipynb`](../main.ipynb)
   ```python
   import os
   from genai.client import generate_texture

   input_mesh = "3dmodel/duck/duck_model_3.obj"
   output_directory = "output/"

   prompt = "A cartoon styled batman duck with a batman logo on the side"
   negative_prompt = "realistic, ugly, deformed, blurry, bad anatomy"
   prompt_wrapper = None # additional instructions appended after the prompt

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
