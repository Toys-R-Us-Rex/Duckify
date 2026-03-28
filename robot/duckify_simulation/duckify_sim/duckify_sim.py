"""DuckifySim -- drop-in replacement for ISCoin that talks to Gazebo.

Author:     Pierre-Yves Savioz, with assistance from Claude AI (Anthropic)
Course:     HES-SO Valais-Wallis, Engineering Track 304
Inspired:   API modelled on ISCoin by Axel Amand, HES-SO (MIT License, 2024)
"""

import subprocess

from . import ros_bridge
from .robot_control import SimRobotControl


class DuckifySim:
    """Drop-in replacement for ISCoin that talks to the Gazebo simulator."""

    def __init__(self, container_name="iscoin_simulator"):
        ros_bridge.CONTAINER_NAME = container_name

        # Check that the container is running
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", container_name],
            capture_output=True,
            text=True,
        )
        if "true" not in result.stdout:
            raise ConnectionError(
                f"Container '{container_name}' is not running. "
                "Start the simulator first:\n"
                "  cd ur3e-simulator/.docker && docker compose run --rm cpu\n"
                "  ros2 launch iscoin_simulation_gz iscoin_sim_control.launch.py"
            )

        self._robot_control = SimRobotControl()
        print(f"DuckifySim connected to container '{container_name}'")

    @property
    def robot_control(self):
        return self._robot_control

    @property
    def gripper(self):
        return None

    @property
    def camera(self):
        print("WARNING: Camera is not available in the Gazebo simulator")
        return None

    def close(self):
        print("DuckifySim closed")
