import os
import shutil
import subprocess
from pathlib import Path
import time

class MVAdapaterModel:
    def __init__(self, base_path: Path):
        self.base_path = base_path.resolve()
        self.slurm_script = self.base_path / "script.slurm"
        
        if not self.slurm_script.exists():
            raise FileNotFoundError(f"Le script {self.slurm_script} est introuvable.")

        for d in ["3d_models", "outputs", "logs"]:
            (self.base_path / d).mkdir(parents=True, exist_ok=True)

    def run(self, text_prompt: str, obj_file: Path, negative_prompt: str = "", prompt_wrapper: str = "", steps: int = 30, guidance: float = 6.0) -> Path:
        if not obj_file.exists():
            raise FileNotFoundError(f"Fichier 3D introuvable: {obj_file}")

        target_obj_path = self.base_path / "3d_models" / obj_file.name
        if obj_file != target_obj_path:
            shutil.copy(obj_file, target_obj_path)

        run_id = f"gen_{int(time.time())}"
        output_dir = self.base_path / "outputs" / run_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        save_name = f"textured_{obj_file.stem}"

        final_prompt = text_prompt
        if prompt_wrapper:
            final_prompt = text_prompt + " " + prompt_wrapper

        env = os.environ.copy()
        env["MV_PROMPT"] = final_prompt
        env["MV_NEG_PROMPT"] = negative_prompt
        env["MV_MESH_PATH"] = f"3d_models/{obj_file.name}"
        env["MV_OUTPUT_DIR"] = f"outputs/{run_id}"
        env["MV_SAVE_NAME"] = save_name
        env["MV_STEPS"] = str(steps)
        env["MV_GUIDANCE"] = str(guidance)

        print(f"Soumission du job SLURM pour la génération {run_id}...")
        
        try:
            result = subprocess.run(
                ["sbatch", "--wait", str(self.slurm_script)], 
                env=env,
                cwd=str(self.base_path),
                capture_output=True,
                text=True,
                check=True
            )
            print(f"Job soumis : {result.stdout.strip()}")
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error : {e.stderr}")

        return output_dir
