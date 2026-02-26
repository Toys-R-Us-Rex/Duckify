import os
import shutil
import uuid
import zipfile
import io
from pathlib import Path
from flask import Flask, request, send_file, jsonify
from dotenv import load_dotenv


from source.model import TextureModel

load_dotenv()

app = Flask(__name__)

HF_TOKEN = os.environ.get("hf_token")
if not HF_TOKEN:
    raise ValueError("Le token HF est manquant dans le fichier .env")

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

    if file.filename == '':
        return jsonify({"error": "Nom de fichier vide"}), 400

    job_id = str(uuid.uuid4())
    current_job_path = JOBS_DIR / job_id
    current_job_path.mkdir(parents=True, exist_ok=True)

    try:
        input_filename = file.filename
        safe_filename = os.path.basename(input_filename)
        input_path = current_job_path / safe_filename
        file.save(input_path)

        print(f"[{job_id}] Démarrage du job pour : {prompt}")
        texture_model = TextureModel(base_path=current_job_path, hf_token=HF_TOKEN)

        experiment_path = texture_model.run(text_prompt=prompt, obj_file=input_path)

        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # On parcourt récursivement le dossier experiment_path
            for root, dirs, files in os.walk(experiment_path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    # On ajoute le fichier au zip en gardant une structure propre
                    # arcname permet de ne pas avoir toute l'arborescence absolue dans le zip
                    arcname = os.path.relpath(file_path, start=experiment_path)
                    zf.write(file_path, arcname=arcname)
        
        # On remet le curseur au début du fichier en mémoire
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
        if current_job_path.exists():
            shutil.rmtree(current_job_path)
            print(f"[{job_id}] Nettoyage terminé.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)