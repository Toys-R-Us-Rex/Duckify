# Duckify — Robot Setup Guide

## 1. Load the Gazebo Simulator Docker Image using GHCR

First you need to create a (**classic**, not fine grained) personal access token [here](https://github.com/settings/tokens).

> [!IMPORTANT]
> Make sure to check the `read:packages` scope before generating the token.

Once created, copy it and login to ghrc.io through docker:

```bash
export GITHUB_TOKEN=your_github_token
echo $GITHUB_TOKEN | docker login ghcr.io -u GithubUsername --password-stdin
```

Then pull the docker image:
```bash
docker pull ghcr.io/toys-r-us-rex/iscoin-simulator:v1.0.0
```
Verify it pulled:

```bash
docker images | grep iscoin
```

## 2. Start the simulator

The `docker-compose.yml` is inside `robot/docker/`, not at the repo root.

```bash
cd ./robot/docker
docker compose run --rm --name iscoin_simulator cpu
```

> [!INFO]
> Use `gpu` instead of `cpu` if you have an NVIDIA GPU with nvidia-container-toolkit.

> [!INFO]
> Also, remove the `--rm` flag if you wish to modify files inside the container

### XAUTHORITY issue

If you have an issue with Xauthority when running gazebo try doing the following (for linux):

```sh
touch ~/.Xauthority
export XAUTHORITY=~/.Xauthority
```

## 3. Install PyBullet

When running `uv sync`, an error might appear when installing/building PyBullet:

```sh
    [stderr]
    C:\Users\xxx\AppData\Local\uv\cache\builds-v0.tmplC4i5R\Lib\site-packages\setuptools\dist.py:765: SetuptoolsDeprecationWarning: License classifiers are deprecated.
    !!
            **
            Please consider removing the following classifiers in favor of a SPDX license expression:
            License :: OSI Approved :: zlib/libpng License
            See https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#license for details.
            **
    !!
    self._finalize_license_expression()
    error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/

    hint: This usually indicates a problem with the package or the build environment.
help: pybullet (v3.2.7) was included because duckify (v0.1.0) depends on robot (v0.1.0) which depends on pybullet
```

Meaning you might need to install a C++ compiler on Windows machines. You can download the [Visual Studio Build Tools C++](https://visualstudio.microsoft.com/visual-cpp-build-tools/) to be able to build PyBullet locally.

## 4. Launch Gazebo inside the container

Once inside the container shell:

```bash
ros2 launch iscoin_simulation_gz iscoin_sim_control.launch.py
```

## 5. Send commands to the simulator

Open a second terminal on the host and enter the running container:

```bash
docker exec -it iscoin_simulator /bin/bash
```

Run the demo trajectory:

```bash
ros2 run iscoin_driver demo.py
```

Or a custom trajectory:

```bash
ros2 run iscoin_driver demo.py --ros-args -p traj:=<path-to>/custom_traj.json
```

## Fix Wayland/Hyprland display forwarding

The simulator uses Gazebo GUI which needs X11. On Hyprland (Wayland), you need XWayland forwarding.

Install xhost:

```bash
sudo pacman -S xorg-xhost
```

Allow Docker to access your display (run this every session, or add to your shell rc):

```bash
xhost +local:docker
```

## Quick reference — stop everything

- `CTRL+C` in the Gazebo terminal to stop the simulator
- `exit` to leave the container
- The `--rm` flag auto-removes the container when it stops
