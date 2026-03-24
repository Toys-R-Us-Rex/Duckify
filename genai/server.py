import io
import os
import shutil
import uuid
import zipfile
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from pydantic import ValidationError
from models import MVAdapaterModel

from genai.data import GenerationRequest

app = Flask(__name__)


MV_ADAPTER_DIR = Path(os.getenv("MV_ADAPTER_PATH", None))

if not MV_ADAPTER_DIR.exists():
    raise ValueError(f"Le dossier MV-Adapter est introuvable : {MV_ADAPTER_DIR}")

JOBS_DIR = Path("jobs_temp")
JOBS_DIR.mkdir(exist_ok=True)


@app.post("/generate")
def generate_texture():
    req: GenerationRequest
    
    try:
        req = GenerationRequest.model_validate(
            request.form, extra="ignore"
        )
        file = request.files.get("file", None)
        assert file is not None
    except (ValidationError, AssertionError):
        return jsonify({"Error": "Missing or invalid parameters"}), 400

    job_id = str(uuid.uuid4())
    current_job_path = JOBS_DIR / job_id
    current_job_path.mkdir(parents=True, exist_ok=True)

    experiment_path = None
    input_filename = file.filename
    safe_filename = Path(input_filename).name
    input_path = current_job_path / safe_filename
    file.save(input_path)

    print(f"[{job_id}] Démarrage du job SLURM | Steps: {req.steps} | Guidance: {req.guidance}")
    try:
        texture_model = MVAdapaterModel(
            base_path=MV_ADAPTER_DIR, slurm_script=Path("run.slurm")
        )

        experiment_path = texture_model.run(
            text_prompt=req.prompt,
            obj_file=input_path,
            negative_prompt=req.negative_prompt,
            prompt_wrapper=req.prompt_wrapper,
            steps=req.steps,
            guidance=req.guidance,
            hf_token=req.hf_token,
        )

        print(f"[{job_id}] Génération SLURM terminée. Préparation du zip...")

        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(experiment_path):
                for filename in files:
                    file_path = Path(root) / filename
                    arcname = file_path.relative_to(experiment_path)
                    zf.write(file_path, arcname=arcname)

        memory_file.seek(0)

        print(f"[{job_id}] Succès ! Envoi du zip.")

        return send_file(
            memory_file,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"texture_result_{job_id}.zip",
        )

    except Exception as e:
        print(f"[{job_id}] Erreur : {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if current_job_path.exists():
            try:
                shutil.rmtree(current_job_path)
            except Exception as cleanup_error:
                print(f"[{job_id}] Erreur nettoyage upload : {cleanup_error}")

        if experiment_path and experiment_path.exists():
            try:
                shutil.rmtree(experiment_path)
                print(f"[{job_id}] Nettoyage des résultats MV-Adapter terminé.")
            except Exception as cleanup_error:
                print(f"[{job_id}] Erreur nettoyage résultats : {cleanup_error}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
