import os
import shutil
import subprocess
from pathlib import Path
import time

class MVAdapaterModel:
    def __init__(
        self,
        base_path: Path,
        slurm_script: Path,
        docker_image: str = "mv-adapter:latest",
        docker_auto_build: bool = True,
        docker_container_name: str = "mv-adapter-runtime",
    ):
        self.base_path = base_path.resolve()
        self.docker_image = docker_image
        self.docker_auto_build = docker_auto_build
        self.docker_container_name = docker_container_name
        self.slurm_script = slurm_script.resolve()
        dockerfile_path = self.base_path / "Dockerfile"
        if not dockerfile_path.exists() and self.docker_auto_build:
            raise FileNotFoundError(
                f"Dockerfile not found: {dockerfile_path}. "
                "Create it or disable docker_auto_build."
            )
        if not self.slurm_script.exists():
            raise FileNotFoundError(f"SLURM script not found: {self.slurm_script}")
        

        for d in ["assets", "outputs", "logs"]:
            (self.base_path / d).mkdir(parents=True, exist_ok=True)

    def _docker_image_exists(self) -> bool:
        result = subprocess.run(
            ["docker", "image", "inspect", self.docker_image],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0

    def _ensure_docker_image(self) -> None:
        if self._docker_image_exists():
            return

        if not self.docker_auto_build:
            raise RuntimeError(
                f"Docker image '{self.docker_image}' not found and docker_auto_build=False"
            )

        print(f"Docker image missing. Building '{self.docker_image}'...")
        build_cmd = [
            "docker",
            "build",
            "-t",
            self.docker_image,
            "-f",
            str(self.base_path / "Dockerfile"),
            str(self.base_path),
        ]
        build_result = subprocess.run(
            build_cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        if build_result.returncode != 0:
            raise RuntimeError(
                "MV-Adapter Docker build failed:\n"
                f"STDOUT:\n{build_result.stdout}\n"
                f"STDERR:\n{build_result.stderr}"
            )

    def _docker_container_exists(self) -> bool:
        result = subprocess.run(
            ["docker", "container", "inspect", self.docker_container_name],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0

    def _docker_container_running(self) -> bool:
        result = subprocess.run(
            [
                "docker",
                "container",
                "inspect",
                "-f",
                "{{.State.Running}}",
                self.docker_container_name,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0 and result.stdout.strip().lower() == "true"

    def _ensure_runtime_container(self) -> None:
        if self._docker_container_exists():
            if self._docker_container_running():
                return

            print(f"Starting existing container '{self.docker_container_name}'...")
            start_result = subprocess.run(
                ["docker", "start", self.docker_container_name],
                capture_output=True,
                text=True,
                check=False,
            )
            if start_result.returncode != 0:
                raise RuntimeError(
                    "Failed to start MV-Adapter runtime container:\n"
                    f"STDOUT:\n{start_result.stdout}\n"
                    f"STDERR:\n{start_result.stderr}"
                )
            return

        print(f"Creating runtime container '{self.docker_container_name}'...")
        create_result = subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--gpus",
                "all",
                "--name",
                self.docker_container_name,
                "-v",
                f"{self.base_path}:/workspace",
                "-w",
                "/workspace",
                self.docker_image,
                "tail",
                "-f",
                "/dev/null",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if create_result.returncode != 0:
            raise RuntimeError(
                "Failed to create MV-Adapter runtime container:\n"
                f"STDOUT:\n{create_result.stdout}\n"
                f"STDERR:\n{create_result.stderr}"
            )

    def prepare_runtime(self) -> None:
        self._ensure_docker_image()
        self._ensure_runtime_container()

    def _run_sbatch(
        self,
        final_prompt: str,
        negative_prompt: str,
        asset_mesh_path: str,
        output_dir_rel: str,
        save_name: str,
        steps: int,
        guidance: float,
        hf_token: str,
    ) -> None:
        self.prepare_runtime()

        env = os.environ.copy()
        env["MV_ADAPTER_PATH"] = str(self.base_path)
        env["MV_DOCKER_CONTAINER_NAME"] = self.docker_container_name
        env["MV_MESH_PATH"] = asset_mesh_path
        env["MV_PROMPT"] = final_prompt
        env["MV_OUTPUT_DIR"] = output_dir_rel
        env["MV_SAVE_NAME"] = save_name
        env["MV_STEPS"] = str(steps)
        env["MV_GUIDANCE"] = str(guidance)
        env["MV_NEGATIVE_PROMPT"] = negative_prompt
        env["HF_TOKEN"] = hf_token

        sbatch_cmd = ["sbatch", "--wait", str(self.slurm_script)]
        result = subprocess.run(
            sbatch_cmd,
            cwd=str(self.base_path),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(
                "MV-Adapter SBATCH execution failed:\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )

    def run(self, text_prompt: str, obj_file: Path, negative_prompt: str = "", prompt_wrapper: str = "", steps: int = 30, guidance: float = 6.0,HF_TOKEN="") -> Path:
        if not obj_file.exists():
            raise FileNotFoundError(f"3D file not found: {obj_file}")

        docker_asset_path = self.base_path / "assets" / obj_file.name
        if obj_file != docker_asset_path:
            shutil.copy(obj_file, docker_asset_path)

        run_id = f"gen_{int(time.time())}"
        output_dir = self.base_path / "outputs" / run_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        save_name = f"textured_{obj_file.stem}"

        final_prompt = text_prompt
        if prompt_wrapper:
            final_prompt = text_prompt + " " + prompt_wrapper

        print(f"Submitting SLURM job for generation {run_id}...")
        self._run_sbatch(
            final_prompt=final_prompt,
            negative_prompt=negative_prompt,
            asset_mesh_path=f"assets/{obj_file.name}",
            output_dir_rel=f"outputs/{run_id}",
            save_name=save_name,
            steps=steps,
            guidance=guidance,
            hf_token=HF_TOKEN,
        )

        return output_dir
