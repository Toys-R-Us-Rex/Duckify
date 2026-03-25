# HES_Duckify — UR3e Setup Guide

## 1. Load the Docker image

### Using the .zip
Find the docker image [here](https://www.swisstransfer.com/d/fc9eed52-3be8-40a9-a09c-c213bb549d4e)

```bash
docker load < iscoin-simulator-0.1.0.tar.gz
```

Verify it loaded:

```bash
docker images | grep iscoin
```

### Using GHCR

First you need to create a (classic, not fine grained) personal access token [here](https://github.com/settings/tokens).

> [!IMPORTANT]
> Make sure to check the `read:packages` scope before generating the token.

Once created, copy it and login to ghrc.io through docker:

```bash
export GITHUB_TOKEN=your_github_token
echo $GITHUB_TOKEN | docker login ghcr.io -u GithubUsername --pasword-stdin
```

Then pull the docker image:
```bash
docker pull ghcr.io/toys-r-us-rex/duckify:iscoin-simulator
```
Verify it pulled:

```bash
docker images | grep iscoin
```

## 2. Fix Wayland/Hyprland display forwarding

The simulator uses Gazebo GUI which needs X11. On Hyprland (Wayland), you need XWayland forwarding.

Install xhost:

```bash
sudo pacman -S xorg-xhost
```

Allow Docker to access your display (run this every session, or add to your shell rc):

```bash
xhost +local:docker
```

## 3. Start the simulator

The `docker-compose.yml` is inside `robot/.docker/`, not at the repo root.

```bash
cd ./robot/.docker
docker compose run --rm --name iscoin_simu lator cpu
```

> Use `gpu` instead of `cpu` if you have an NVIDIA GPU with nvidia-container-toolkit.

> Also, remove the `--rm` flag if you wish to modify files inside the container

## 4. Test pybullet

To test if pybullet is working on your machine, run the following command:
```bash
python -c "import pybullet; client = pybullet.connect(pybullet.DIRECT); print(f'PyBullet {pybullet.getAPIVersion()} is working!'); pybullet.disconnect(client)"
```

If this test doesn't work, you might need to install a C++ compiler, because pybullet doesn't have a compiled version for the current python version. 

### Windows
You can download the [Visual Studio Build Tools C++](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

### Fedora:
```bash
sudo dnf install python3-devel gcc-c++ mesa-libGL-devel mesa-libGLU-devel
```

Retry the test command to verify.


## 5. Launch Gazebo inside the container

Once inside the container shell:

```bash
ros2 launch iscoin_simulation_gz iscoin_sim_control.launch.py
```

### .Xauthority issue

If you have an issue with Xauthority when running gazebo try doing the following (for linux):

touch 

## 6. Send commands to the simulator

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

## Quick reference — stop everything

- `CTRL+C` in the Gazebo terminal to stop the simulator
- `exit` to leave the container
- The `--rm` flag auto-removes the container when it stops
