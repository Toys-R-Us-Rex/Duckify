import docker
import shutil
from pathlib import Path
from typing import Optional
from docker.types import DeviceRequest



class TextureModel:
    GITHUB_REPO = "ghcr.io/toys-r-us-rex/texturepaper:latest"
    def __init__(
        self,
        base_path: Path,
        hf_token: str,
        gh_user: str,
        gh_token: str
    ):
        self.base_path = base_path
        self.gh_user = gh_user
        self.gh_token = gh_token
        
        self.client = docker.from_env()

        (base_path / "shapes").mkdir(parents=True, exist_ok=True)
        (base_path / "configs").mkdir(exist_ok=True)
        (base_path / "experiments").mkdir(exist_ok=True)

        (base_path / "TOKEN").write_text(hf_token)
        print("Connexion à GitHub Container Registry (ghcr.io)...")
        self.client.login(username=self.gh_user, password=self.gh_token, registry="ghcr.io")

        print("Pull de l'image Docker...")
        self.image = self.client.images.pull(self.GITHUB_REPO)
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

        config_yaml = f"""prompt: "{text_prompt}"
        mesh_path: "shapes/{obj_file.name}"
        """
        config_path = self.base_path / "configs" / "run.yaml"
        config_path.write_text(config_yaml)
        
        # Run container
        print("Démarrage du conteneur...")
        container = self.client.containers.run(
            self.GITHUB_REPO,
            detach=True,
            volumes={
                str(self.base_path.resolve()): {"bind": "/workspace", "mode": "rw"}
            },
            device_requests=[
                DeviceRequest(count=-1, capabilities=[["gpu"]]) # using gpu
            ]
        )

        print("Container started:", container.id)

        try:
            # Wait for completion
            result = container.wait()
            logs = container.logs().decode()

            print("Exit code:", result["StatusCode"])
            print("Logs:\n", logs)

            if result["StatusCode"] != 0:
                raise RuntimeError(f"TEXTure failed with exit code {result['StatusCode']}")
                
        finally:
            # Le conteneur sera supprimé même si le code plante avant
            container.remove()

        return self.base_path / "experiments"