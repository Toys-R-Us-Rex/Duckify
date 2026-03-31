import io
import logging
import os
import shutil
import uuid
import zipfile
from logging import Logger
from pathlib import Path

import numpy as np
import trimesh
import trimesh.exchange.gltf
from flask import Flask, jsonify, request, send_file
from models import MVAdapaterModel
from pydantic import ValidationError
from trimesh import Scene

from genai.data import GenerationRequest

app = Flask(__name__)
logger: Logger = logging.getLogger("GenAIServer")


if "MV_ADAPTER_PATH" not in os.environ:
    raise RuntimeError("Environment variable MV_ADAPTER_PATH is not set")

MV_ADAPTER_DIR = Path(os.environ.get("MV_ADAPTER_PATH", "")).resolve()

if not MV_ADAPTER_DIR.exists():
    raise FileNotFoundError(f"MV-Adapter could not be found at {MV_ADAPTER_DIR}")

JOBS_DIR = Path("jobs_temp")
JOBS_DIR.mkdir(exist_ok=True)

PORT = int(os.environ.get("API_PORT", 5000))


def obj_to_glb(obj_path: Path, glb_path: Path):
    if obj_path.suffix == ".glb":
        return
    scene: Scene = trimesh.load_scene(obj_path, force=True)

    # Changes axes: Y+ forward / Z+ up -> Z- forward / Y+ up
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=np.radians(-90), direction=[1, 0, 0], point=[0, 0, 0]
    )
    scene.apply_transform(rotation_matrix)
    bounds_min, bounds_max = scene.bounds
    translation_matrix = trimesh.transformations.translation_matrix(-bounds_min - (bounds_max - bounds_min) / 2.0)
    scene.apply_transform(translation_matrix)
    with open(glb_path, "wb") as f:
        data: bytes = trimesh.exchange.gltf.export_glb(scene)
        f.write(data)


@app.get("/ping")
def ping():
    return "pong"


@app.post("/generate")
def generate_texture():
    req: GenerationRequest

    try:
        req = GenerationRequest.model_validate(request.form, extra="ignore")
        file = request.files.get("file", None)
        assert file is not None
    except (ValidationError, AssertionError):
        return jsonify({"error": "Missing or invalid parameters"}), 400

    job_id = str(uuid.uuid4())
    current_job_path = JOBS_DIR / job_id
    current_job_path.mkdir(parents=True, exist_ok=True)

    experiment_path = None
    input_filename = file.filename or "model.obj"
    safe_filename = Path(input_filename).name
    obj_path: Path = current_job_path / safe_filename
    file.save(obj_path)

    glb_path: Path = obj_path.parent / f"{obj_path.stem}.glb"
    obj_to_glb(obj_path, glb_path)

    logger.info(
        f"[{job_id}] Starting SLURM job | Steps: {req.steps} | Guidance: {req.guidance}"
    )
    try:
        texture_model = MVAdapaterModel(
            base_path=MV_ADAPTER_DIR, slurm_script=Path("run.slurm")
        )

        experiment_path = texture_model.run(
            text_prompt=req.prompt,
            glb_file=glb_path,
            negative_prompt=req.negative_prompt,
            prompt_wrapper=req.prompt_wrapper,
            steps=req.steps,
            guidance=req.guidance,
            hf_token=req.hf_token,
            num_generations=req.num_generations,
            benchmark_activated=req.benchmark_activated,
        )

        logger.info(f"[{job_id}] Generation finished. Preparing zip...")

        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(experiment_path):
                for filename in files:
                    file_path = Path(root) / filename
                    arcname = file_path.relative_to(experiment_path)
                    zf.write(file_path, arcname=arcname)

        memory_file.seek(0)

        logger.info(f"[{job_id}] Sending zip")

        return send_file(
            memory_file,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"texture_result_{job_id}.zip",
        )

    except Exception as e:
        logger.error(f"[{job_id}] Error: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if current_job_path.exists():
            try:
                shutil.rmtree(current_job_path)
            except Exception as cleanup_error:
                logger.error(
                    f"[{job_id}] Error while cleaning job directory: {cleanup_error}"
                )

        if experiment_path and experiment_path.exists():
            try:
                shutil.rmtree(experiment_path)
                logger.info(f"[{job_id}] Cleanup finished")
            except Exception as cleanup_error:
                logger.error(
                    f"[{job_id}] Error while cleaning experiment directory: {cleanup_error}"
                )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
