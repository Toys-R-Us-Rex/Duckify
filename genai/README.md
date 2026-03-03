# GenAI Pipeline Setup

This project sets up a client-server pipeline to generate AI-driven textures for 3D meshes using the TEXTure model (Dockerized). The client securely sends a mesh and a text prompt to a remote GPU server, which processes it and returns a fully textured 3D model.


## Pipeline 

![GenAI - Pipeline](img_pipeline.png)

### How the Pipeline Works:

1. **Client Execution**: The client script ([client.py](client.py)) runs locally. It opens an SSH tunnel to the inference server ([app.py](app.py)).

2. **API Request**: Through this tunnel, the client sends your .obj file and text prompt to the server's `/generate` endpoint.

3. **AI Processing**: The API receives the inputs and runs a Docker container to generate the texture.

4. **Result Delivery**: Once the rendering is done, the API packages the newly generated artifacts and sends them back to the client.


## Prerequisites

Before starting, ensure you have:
- **[uv](https://docs.astral.sh/uv/)** installed on both your local machine and the server.
- **Docker** installed and running on the remote server (with NVIDIA GPU support).
- **SSH Access** configured from your local machine to the remote server.

---

## Configuration

### You have to create a `.env` file in the folder *genai* (see the example in *.env.example*):

- `HF_TOKEN` : Access token from HuggingFace (to download the AI models).
- `GH_USER` : GitHub username.
- `GH_TOKEN` : GitHub personal access token.

> **💡 How to generate a `GH_TOKEN`:**
> 1. Go to https://github.com/settings/tokens
> 2. Click on **Generate new token** -> **Generate new token (classic)**.
> 3. Give it a name, and **check the `read:packages` scope**.
> 4. Generate and copy the token into your `.env` file.

---

## How to run?

The pipeline requires the server to be listening before the client sends the request.

### 1. Start the Server
You have to run the server file `genai/app.py` on the remote server (e.g., *calypso*) using this command (inside the `genai` directory):

    uv run app.py

*The server will start on port 5000 and wait for incoming requests.*

### 2. Run the Client
You have to run the file `genai/client.py` on your local computer using this command (inside the `genai` directory): 

    uv run client.py

*The client will automatically open an SSH tunnel, send your `.obj` file and prompt, and wait for the generation to complete.*

---

## Expected Output

Once the AI finishes generating the textures:
1. The server packs the results into a ZIP file.
2. The client downloads and automatically extracts this ZIP.
3. You will find a new folder named `extracted_YYYYMMDD_HHMMSS` on your local machine.
4. Inside, navigate to the `experiment_api/mesh` directory to find your newly generated `.obj`, `.mtl`, and texture `.png` files!

*Note: The first run might take a bit longer as the server needs to download the Docker image and the HuggingFace AI models. These models are cached locally, so subsequent runs will be much faster.*