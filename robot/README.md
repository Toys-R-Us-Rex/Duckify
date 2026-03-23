# ur-control
A Python lib to control:
- a Universal Robots UR3-e arm
- a Robotiq Hand-Wrist Camera
- a Robotiq Two Fingers Adaptive Gripper

## Usage
Open the given Jupyter notebook to get a quick library overview:

- [ISCoin](ISCoin.ipynb): simple tests for the three modules
- [CamSettings](CamSettings.ipynb): a demonstrator to manually modify the camera 

## Install

### Poetry 

This codebase uses [uv](https://docs.astral.sh/uv/getting-started/installation/) for dependency management.

From the repository's top-level, run
```bash
uv sync
```

The virtual python environment can then be activated by running `source .venv/bin/activate`.

## Forks
Basecode is a fork of https://github.com/Mandelbr0t/UniversalRobot-Realtime-Control/tree/master.

## Credits
* [AMA](https://people.hes-so.ch/fr/profile/4756082430-axel-amand)
* [RIU](https://people.hes-so.ch/fr/profile/2314729-murielle-richard)