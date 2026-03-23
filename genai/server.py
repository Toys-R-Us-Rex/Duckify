import os
import shutil
import uuid
import zipfile
import io
from pathlib import Path
from flask import Flask, request, send_file, jsonify
from dotenv import load_dotenv
from pyparsing import Optional

from models import MVAdapaterModel


app = Flask(__name__)


MV_ADAPTER_DIR = Path(os.getenv("MV_ADAPTER_PATH",None))

if not MV_ADAPTER_DIR.exists():
        raise ValueError(f"Le dossier MV-Adapter est introuvable : {MV_ADAPTER_DIR}")

JOBS_DIR = Path("jobs_temp")
JOBS_DIR.mkdir(exist_ok=True)

@app.route("/generate", methods=["POST"])
def generate_texture():
    try:
        file = request.files.get("file",None)
        prompt = request.form.get("prompt",None)
        negative_prompt = request.form.get("negative_prompt","")
        prompt_wrapper = request.form.get("prompt_wrapper","")
        HF_TOKEN = request.form.get("HF_TOKEN","")
        
        steps = int(request.form.get("steps", 30))
        guidance = float(request.form.get("guidance", 6.0))

        if not all([file, prompt]):
            return jsonify({"Error":"File and prompt are required"}), 400

        job_id = str(uuid.uuid4())
        current_job_path = JOBS_DIR / job_id
        current_job_path.mkdir(parents=True, exist_ok=True)
        
        experiment_path = None 
        input_filename = file.filename
        safe_filename = Path(input_filename).name
        input_path = current_job_path / safe_filename
        file.save(input_path)

        print(f"[{job_id}] Démarrage du job SLURM | Steps: {steps} | Guidance: {guidance}")
        
        texture_model = MVAdapaterModel(base_path=MV_ADAPTER_DIR,slurm_script=Path("run.slurm"))

        experiment_path = texture_model.run(
            text_prompt=prompt, 
            obj_file=input_path,
            negative_prompt=negative_prompt,
            prompt_wrapper=prompt_wrapper,
            steps=steps,
            guidance=guidance,
            HF_TOKEN=HF_TOKEN
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
            download_name=f"texture_result_{job_id}.zip"
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