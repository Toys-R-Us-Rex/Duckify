import docker
import shutil
import textwrap
import urllib.request
import os
from pathlib import Path
from docker.types import DeviceRequest

class TextureModel:
    GITHUB_REPO = "ghcr.io/toys-r-us-rex/texturepaper:0.1.0"
    RAW_REPO_URL = "https://raw.githubusercontent.com/TEXTurePaper/TEXTurePaper/main"

    def __init__(
        self,
        base_path: Path,
        hf_token: str,
        gh_user: str,
        gh_token: str
    ):
        self.base_path = base_path.resolve()
        self.gh_user = gh_user
        self.gh_token = gh_token
        
        self.client = docker.from_env()


        for d in ["shapes", "configs", "experiments", "textures","cache"]:
            path = self.base_path / d
            path.mkdir(parents=True, exist_ok=True)
            os.chmod(path, 0o777)

        (self.base_path / "TOKEN").write_text(hf_token)
        
        # Authentification et Pull
        auth_config = {
            'username': self.gh_user,
            'password': self.gh_token
        }

        print("Connexion à GitHub Container Registry (ghcr.io) et Pull de l'image...")
        self.image = self.client.images.pull(
            self.GITHUB_REPO, 
            auth_config=auth_config
        )
        print("Image ready:", self.image.tags)

    def download_if_lfs(self, source_path: Path, target_path: Path, remote_url: str):
        """Télécharge le fichier si la source est un pointeur LFS ou absente."""
        is_lfs = False
        if source_path.exists():
            with open(source_path, 'r', errors='ignore') as f:
                first_line = f.readline()
                if "version https://git-lfs" in first_line:
                    is_lfs = True
        
        if not source_path.exists() or is_lfs:
            urllib.request.urlretrieve(remote_url, target_path)
        else:
            shutil.copy(source_path, target_path)

    def run(self, text_prompt: str, obj_file: Path) -> Path:
        if not obj_file.exists():
            raise FileNotFoundError(obj_file)

        shutil.copy(obj_file, self.base_path / "shapes" / obj_file.name)

        vendor_base = Path("~/Duckify/vendor/TEXTure").expanduser()
        
        self.download_if_lfs(
            vendor_base / "shapes/env_sphere.obj",
            self.base_path / "shapes/env_sphere.obj",
            f"{self.RAW_REPO_URL}/shapes/env_sphere.obj"
        )

        self.download_if_lfs(
            vendor_base / "textures/brick_wall.png",
            self.base_path / "textures/brick_wall.png",
            f"{self.RAW_REPO_URL}/textures/brick_wall.png"
        )

        config_yaml = textwrap.dedent(f"""\
            log:
              exp_name: experiment_api
            guide:
              text: "{text_prompt}"
              append_direction: True
              shape_path: shapes/{obj_file.name}
            optim:
              seed: 3
        """)
        (self.base_path / "configs" / "run.yaml").write_text(config_yaml)
        

        volumes = {
            str(self.base_path / "TOKEN"): {"bind": "/workspace/TOKEN", "mode": "rw"},
            str(self.base_path / "shapes"): {"bind": "/workspace/shapes", "mode": "rw"},
            str(self.base_path / "configs"): {"bind": "/workspace/configs", "mode": "rw"},
            str(self.base_path / "textures"): {"bind": "/workspace/textures", "mode": "rw"},
            str(self.base_path / "experiments"): {"bind": "/workspace/experiments", "mode": "rw"},
            str(self.base_path / "cache"): {"bind": "/workspace/cache", "mode": "rw"}
        }


        print("Démarrage du conteneur...")
        uid, gid = os.getuid(), os.getgid()

        container = self.client.containers.run(
            self.GITHUB_REPO,
            command="python -m scripts.run_texture --config_path=configs/run.yaml",
            user=f"{uid}:{gid}", 
            detach=True,
            volumes=volumes,
            environment={
                "MPLCONFIGDIR": "/workspace/cache/matplotlib",
                "TRANSFORMERS_CACHE": "/workspace/cache/huggingface",
                "HF_HOME": "/workspace/cache/huggingface"
            },
            device_requests=[
                DeviceRequest(count=-1, capabilities=[["gpu"]])
            ]
        )

        print("Container started:", container.id)

        try:

            for chunk in container.logs(stream=True):
                print(chunk.decode('utf-8'), end='')

            result = container.wait()
            print("\nExit code:", result["StatusCode"])

            if result["StatusCode"] != 0:
                raise RuntimeError(f"TEXTure a échoué avec le code {result['StatusCode']}")
                
        finally:
            # Nettoyage
            container.remove()

        return self.base_path / "experiments"