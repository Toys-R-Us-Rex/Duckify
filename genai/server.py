import os
import shutil
import uuid
import zipfile
import io
from pathlib import Path
from flask import Flask, request, send_file, jsonify
from dotenv import load_dotenv

from models import MVAdapaterModel

load_dotenv()

app = Flask(__name__)

MV_ADAPTER_DIR = Path("/home/kevin.voisin/Duckify/genai/MV-Adapter" ) # Chemin vers le dossier MV-Adapter

if not MV_ADAPTER_DIR.exists():
        raise ValueError(f"Le dossier MV-Adapter est introuvable : {MV_ADAPTER_DIR}")

JOBS_DIR = Path("jobs_temp")
JOBS_DIR.mkdir(exist_ok=True)

@app.route('/generate', methods=['POST'])
def generate_texture():
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier envoyé"}), 400
    if 'prompt' not in request.form:
        return jsonify({"error": "Aucun prompt envoyé"}), 400

    file = request.files['file']
    prompt = request.form['prompt']
    negative_prompt = request.form.get('negative_prompt', '')
    prompt_wrapper = request.form.get('prompt_wrapper', '')
    HF_TOKEN = request.form.get('HF_TOKEN', '')
    
    try:
        steps = int(request.form.get('steps', 30))
    except ValueError:
        steps = 30
        
    try:
        guidance = float(request.form.get('guidance', 6.0))
    except ValueError:
        guidance = 6.0

    if file.filename == '':
        return jsonify({"error": "Nom de fichier vide"}), 400

    job_id = str(uuid.uuid4())
    current_job_path = JOBS_DIR / job_id
    current_job_path.mkdir(parents=True, exist_ok=True)
    
    experiment_path = None 

    try:
        input_filename = file.filename
        safe_filename = os.path.basename(input_filename)
        input_path = current_job_path / safe_filename
        file.save(input_path)

        print(f"[{job_id}] Démarrage du job SLURM | Steps: {steps} | Guidance: {guidance}")
        
        texture_model = MVAdapaterModel(base_path=MV_ADAPTER_DIR)

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
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(experiment_path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    arcname = os.path.relpath(file_path, start=experiment_path)
                    zf.write(file_path, arcname=arcname)
        
        memory_file.seek(0)

        print(f"[{job_id}] Succès ! Envoi du zip.")
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'texture_result_{job_id}.zip'
        )

    except Exception as e:
        print(f"[{job_id}] Erreur : {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        def remove_readonly(func, path, excinfo):
            import stat
            os.chmod(path, stat.S_IWRITE)
            func(path)

        if current_job_path.exists():
            try:
                shutil.rmtree(current_job_path, onerror=remove_readonly)
            except Exception as cleanup_error:
                print(f"[{job_id}] Erreur nettoyage upload : {cleanup_error}")

        if experiment_path and experiment_path.exists():
            try:
                shutil.rmtree(experiment_path, onerror=remove_readonly)
                print(f"[{job_id}] Nettoyage des résultats MV-Adapter terminé.")
            except Exception as cleanup_error:
                print(f"[{job_id}] Erreur nettoyage résultats : {cleanup_error}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)