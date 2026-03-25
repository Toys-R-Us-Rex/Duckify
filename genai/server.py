import io
import os
import shutil
import uuid
import zipfile
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from models import MVAdapaterModel

app = Flask(__name__)


mv_adapter_path = os.getenv("MV_ADAPTER_PATH")
if not mv_adapter_path:
    raise ValueError("MV_ADAPTER_PATH environment variable is required")

MV_ADAPTER_DIR = Path(mv_adapter_path)

if not MV_ADAPTER_DIR.exists():
    raise ValueError(f"MV-Adapter directory not found: {MV_ADAPTER_DIR}")

JOBS_DIR = Path("jobs_temp")
JOBS_DIR.mkdir(exist_ok=True)

TEXTURE_MODEL = MVAdapaterModel(
    base_path=MV_ADAPTER_DIR
)
print("Preparing MV-Adapter Docker runtime...")
TEXTURE_MODEL.prepare_runtime()
print("MV-Adapter Docker runtime is ready.")

@app.route("/generate", methods=["POST"])
def generate_texture():
    file = request.files.get("file",None)
    prompt = request.form.get("prompt",None)
    negative_prompt = request.form.get("negative_prompt","")
    prompt_wrapper = request.form.get("prompt_wrapper","")
    HF_TOKEN = request.form.get("HF_TOKEN","")
    
    steps = int(request.form.get("steps", 30))
    guidance = float(request.form.get("guidance", 6.0))

    if not all([file, prompt]):
        return jsonify({"error": "file and prompt are required"}), 400

    job_id = str(uuid.uuid4())
    current_job_path = JOBS_DIR / job_id
    current_job_path.mkdir(parents=True, exist_ok=True)
    
    experiment_path = None 
    input_filename = file.filename
    safe_filename = Path(input_filename).name
    input_path = current_job_path / safe_filename
    file.save(input_path)

    print(f"[{job_id}] Starting generation (slurm+docker) | Steps: {steps} | Guidance: {guidance}")
    try:
        experiment_path = TEXTURE_MODEL.run(
            text_prompt=prompt, 
            obj_file=input_path,
            negative_prompt=negative_prompt,
            prompt_wrapper=prompt_wrapper,
            steps=steps,
            guidance=guidance,
            HF_TOKEN=HF_TOKEN
        )

        print(f"[{job_id}] Generation completed. Preparing zip...")

        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(experiment_path):
                for filename in files:
                    file_path = Path(root) / filename
                    arcname = file_path.relative_to(experiment_path)
                    zf.write(file_path, arcname=arcname)
        
        memory_file.seek(0)

        print(f"[{job_id}] Success! Sending zip.")
        
        return send_file(
            memory_file,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"texture_result_{job_id}.zip"
        )

    except Exception as e:
        print(f"[{job_id}] Error: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if current_job_path.exists():
            try:
                shutil.rmtree(current_job_path)
            except Exception as cleanup_error:
                print(f"[{job_id}] Upload cleanup error: {cleanup_error}")

        if experiment_path and experiment_path.exists():
            try:
                shutil.rmtree(experiment_path)
                print(f"[{job_id}] MV-Adapter output cleanup completed.")
            except Exception as cleanup_error:
                print(f"[{job_id}] Output cleanup error: {cleanup_error}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)