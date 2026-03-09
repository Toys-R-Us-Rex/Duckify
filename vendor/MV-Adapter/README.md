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

> [!IMPORTANT]
> **TODO**