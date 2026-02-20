# TEXTure: Text-Guided Texturing of 3D Shapes

> TEXTure takes an input mesh and a conditioning text prompt and paints the mesh with high-quality textures, using an iterative diffusion-based process. In the paper we show that TEXTure can be used to not only generate new textures but also edit and refine existing textures using either a text prompt or user-provided scribbles.

## Links
- Website: https://texturepaper.github.io/TEXTurePaper/
- GitHub: https://github.com/TEXTurePaper/TEXTurePaper
- arxiv: https://arxiv.org/abs/2302.01721
- Internal fork: https://github.com/Toys-R-Us-Rex/TEXTurePaper

## Installation

### Getting the image

To get the Docker image, you can either fetch it from the [GitHub package repository](https://github.com/Toys-R-Us-Rex/TEXTurePaper/pkgs/container/texturepaper)
```bash
docker pull ghcr.io/toys-r-us-rex/texturepaper:latest
```

or build it yourself

```bash
git clone https://github.com/Toys-R-Us-Rex/TEXTurePaper.git
cd TEXTurePaper
docker build -t texturepaper:latest .
```

## Running

To run TEXTure, you can use the provided docker compose configuration.

1. Get an access token from Huggingface
2. Put it in a file named `TOKEN`
3. Get a 3D model in `.obj` format. The mesh MUST be triangulated and can contain UV map
4. Put it in a `shapes` directory
5. Put a configuration file in the `configs` directory. An example is provided in [configs/sample.yaml](configs/sample.yaml). For a list of all options, please refer to [this class](https://github.com/Toys-R-Us-Rex/TEXTurePaper/blob/main/src/configs/train_config.py)
6. Run the container
   ```bash
   docker compose up TEXTure
   ```
7. Get the results in the `experiments` folder
