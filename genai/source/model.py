import docker
import shutil
from pathlib import Path
from typing import Optional
from docker.types import DeviceRequest


class TextureModel:
    def __init__(
        self,
        base_path: Path,
        hf_token: str,
    ):
        self.base_path = base_path
        self.client = docker.from_env()

        (base_path / "shapes").mkdir(parents=True, exist_ok=True)
        (base_path / "configs").mkdir(exist_ok=True)
        (base_path / "experiments").mkdir(exist_ok=True)

        (base_path / "TOKEN").write_text(hf_token)

        self.image = self.client.images.pull(
            "ghcr.io/toys-r-us-rex/texturepaper:latest"
        )

        print("Image ready:", self.image.tags)


    def run(self, text_prompt: str, obj_file: Path) -> Path:
        """
        Runs TEXTure on a given .obj mesh and returns the experiment folder path.
        """

        if not obj_file.exists():
            raise FileNotFoundError(obj_file)

        # Copy mesh into shapes/
        mesh_target = self.base_path / "shapes" / obj_file.name
        shutil.copy(obj_file, mesh_target)

        # Create config file
        config_yaml = f"""
        prompt: "{text_prompt}"
        mesh_path: "shapes/{obj_file.name}"
        """

        config_path = self.base_path / "configs" / "run.yaml"
        config_path.write_text(config_yaml)

        # Run container
        container = self.client.containers.run(
            "ghcr.io/toys-r-us-rex/texturepaper:latest",
            detach=True,
            volumes={
                str(self.base_path.resolve()): {"bind": "/workspace", "mode": "rw"}
            },
            device_requests=[
                DeviceRequest(count=-1, capabilities=[["gpu"]]) # using gpu
            ],
            stdout=True,
            stderr=True
        )

        print("Container started:", container.id)

        # Wait for completion
        result = container.wait()
        logs = container.logs().decode()

        print("Exit code:", result["StatusCode"])
        print("Logs:\n", logs)

        container.remove()

        if result["StatusCode"] != 0:
            raise RuntimeError("TEXTure failed")

        return self.base_path / "experiments"