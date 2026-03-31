# Duckify

<p align="center">
    <img src="assets/icon.svg" width="64">
</p>

Duckify is a complete pipeline to decorate a 3D-printed plastic duck using a Universal Robot UR3-e arm from a text prompt.

## Usage

### With UV
1. Install dependecies

   ```sh
   uv sync
   ```

2. Build and run the UI
   ```sh
   uv run build-ui
   uv run start
   ```

### With Docker

1. Run containers
   ```sh
   # To run the UI using the CPU in the Gazebo simulation
   docker compose --profile cpu up -d
   # To run the UI using the (nvidia) GPU in the Gazebo simulation
   docker compose --profile gpu up -d
   ```

2. Stop containers
   ```sh
   docker compose --profile cpu down
   ```

## Requirements
- Python 3.11+
- UV
- *Docker*

## Install

1. Clone this repository with submodules
   ```bash
   git clone --recursive https://github.com/Toys-R-Us-Rex/Duckify.git
   ```
2. Install Robot environment
   - More details in the [Robot README](./robot/README.md)

## Authors
- Alexandre Venturi ([@mastermeter](https://github.com/mastermeter))
- Cédric Mariéthoz ([@mariethoz](https://github.com/mariethoz))
- Jeremy Duc ([@jijiduc](https://github.com/jijiduc))
- Kevin Voisin ([@kevivois](https://github.com/kevivois))
- Louis Heredero ([@LordBaryhobal](https://github.com/LordBaryhobal))
- Marco Caporizzi ([@caporizzi](https://github.com/caporizzi))
- Nathan Antonietti ([@NathanAnto](https://github.com/NathanAnto))
- Pierre-Yves Savioz ([@szpy1950](https://github.com/szpy1950))
