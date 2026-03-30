# Duckify

<p align="center">
    <img src="assets/icon.svg" width="64">
</p>

Duckify is a complete pipeline to decorate a 3D-printed plastic duck using a Universal Robot UR3-e arm from a text prompt.

## Usage

Simply run the following command to start the program:
```bash
uv run start
```

## Requirements
- Python 3.11+
- UV

## Install

1. Clone this repository with submodules
   ```bash
   git clone --recursive https://github.com/Toys-R-Us-Rex/Duckify.git
   ```
2. Install dependencies
   ```bash
   cd Duckify
   uv sync
   ```
3. Install Robot environment
   - More details in the [Robot README](./robot/README.md)

4. Build PyQt ui files
   ```bash
   uv run build-ui
   ```

## Authors
- Alexandre Venturi ([@mastermeter](https://github.com/mastermeter))
- Cédric Mariéthoz ([@mariethoz](https://github.com/mariethoz))
- Jeremy Duc ([@jijiduc](https://github.com/jijiduc))
- Kevin Voisin ([@kevivois](https://github.com/kevivois))
- Louis Heredero ([@LordBaryhobal](https://github.com/LordBaryhobal))
- Marco Caporizzi ([@caporizzi](https://github.com/caporizzi))
- Nathan Antonietti ([@NathanAnto](https://github.com/NathanAnto))
- Pierre-Yves Savioz ([@szpy1950](https://github.com/szpy1950))
