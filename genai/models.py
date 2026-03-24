import logging
import os
import shutil
import subprocess
import time
from logging import Logger
from pathlib import Path
from typing import Optional


class MVAdapaterModel:
    def __init__(self, base_path: Path, slurm_script: Path):
        self.logger: Logger = logging.getLogger("MVAdapter")
        self.base_path = base_path.resolve()
        script_path = Path(slurm_script)
        if script_path.is_absolute():
            self.slurm_script = script_path
        else:
            self.slurm_script = (
                Path(__file__).resolve().parent / script_path
            ).resolve()

        if not self.slurm_script.exists():
            raise FileNotFoundError(
                f"Le script SLURM est introuvable: {self.slurm_script}"
            )

        for d in ["3d_models", "outputs", "logs"]:
            (self.base_path / d).mkdir(parents=True, exist_ok=True)

    def run(
        self,
        text_prompt: str,
        glb_file: Path,
        negative_prompt: str = "",
        prompt_wrapper: str = "",
        steps: int = 30,
        guidance: float = 6.0,
        hf_token: Optional[str] = "",
        num_generations:int = 1
    ) -> Path:
        if not glb_file.exists():
            raise FileNotFoundError(f"Could not find 3D model: {glb_file}")

        target_obj_path = self.base_path / "3d_models" / glb_file.name
        if glb_file != target_obj_path:
            shutil.copy(glb_file, target_obj_path)

        run_id = f"gen_{int(time.time())}"
        output_dir = self.base_path / "outputs" / run_id
        output_dir.mkdir(parents=True, exist_ok=True)

        save_name = f"textured_{glb_file.stem}"

        final_prompt = text_prompt
        if prompt_wrapper:
            final_prompt = text_prompt + " " + prompt_wrapper

        env = os.environ.copy()
        env["MV_PROMPT"] = final_prompt
        env["MV_NEG_PROMPT"] = negative_prompt
        env["MV_MESH_PATH"] = f"3d_models/{glb_file.name}"
        env["MV_OUTPUT_DIR"] = f"outputs/{run_id}"
        env["MV_SAVE_NAME"] = save_name
        env["MV_STEPS"] = str(steps)
        env["MV_GUIDANCE"] = str(guidance)
        env["MV_NEGATIVE_PROMPT"] = negative_prompt
        env["NUM_GENERATIONS"] = str(num_generations)
        if hf_token is not None:
            env["HF_TOKEN"] = hf_token

        self.logger.info(f"Submitting SLURM job {run_id}...")

        try:
            result = subprocess.run(
                ["sbatch", "--wait", str(self.slurm_script)],
                env=env,
                cwd=str(self.base_path),
                capture_output=True,
                text=True,
                check=True,
            )
            self.logger.info(f"Job submitted: {result.stdout.strip()}")

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error : {e.stderr}")

        return output_dir
