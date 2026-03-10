# MV-Adapter: Multi-view Consistent Image Generation Made Easy

> TEXTure takes an input mesh and a conditioning text prompt and paints the mesh with high-quality textures, using an iterative diffusion-based process. In the paper we show that TEXTure can be used to not only generate new textures but also edit and refine existing textures using either a text prompt or user-provided scribbles.

## Links
- Website: https://huanngzh.github.io/MV-Adapter-Page/
- GitHub: https://github.com/huanngzh/MV-Adapter
- arxiv: https://arxiv.org/abs/2412.03632
- Internal fork: https://github.com/Toys-R-Us-Rex/MV-Adapter

## Installation

### Getting the image

To get the Docker image, you can either fetch it from the [GitHub package repository](https://github.com/Toys-R-Us-Rex/MV-Adapter/pkgs/container/mv-adapter)
```bash
docker pull ghcr.io/toys-r-us-rex/mv-adapter:latest
```

or build it yourself

```bash
git clone https://github.com/Toys-R-Us-Rex/MV-Adapter.git
cd MV-Adapter
docker build -t mv-adapter:latest .
```

## Running

To run MV-Adapter, you can use the provided docker compose configuration.

1. Copy `.env.template` as `.env` and put in an access token from Huggingface
2. Start the container
   ```bash
   docker compose up -d MV-Adapter
   ```

The container will keep running indefinitely. You can then either run a bash terminal or your command directly in it:

- Running a bash terminal
  ```bash
  docker exec -it MV-Adapter /bin/bash
  ```

- Directly running your command
  ```bash
  docker exec MV-Adapter python -m scripts.texture_t2tex \
    --variant sd21 \
    --mesh assets/sphere.glb \
    --text "The Earth, in a minimalist style, with vibrant colors and well defined continents" \
    --save_dir outputs --save_name earth
  ```

> [!WARNING]
> When running a command the first time, it may take some time to download the needed models from Huggingface. Additionally, if the container is removed, so will the HF cache, and the models will need to be downloaded again

### Assets and results

You can put your assets (3D model in `.glb` format) in the `assets` directory.
The results can be retrieved in the `outputs` folder.\
Both folders are mounted as volumes by the docker compose configuration.
