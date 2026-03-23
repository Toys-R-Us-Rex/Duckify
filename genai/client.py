import os
import requests
from sshtunnel import SSHTunnelForwarder
import zipfile
import datetime
from pathlib import Path

def generate_texture(fichier_obj, prompt, output_dir,negative_prompt=None,prompt_wrapper=None,steps=30, guidance=6.0,SSH_HOST=None, SSH_USER=None, SSH_KEY_PATH=None, HF_TOKEN=None):
    print("Connexion SSH...")
    try:
        with SSHTunnelForwarder(
            (SSH_HOST, 22),
            ssh_username=SSH_USER,
            ssh_pkey=SSH_KEY_PATH,
            remote_bind_address=("127.0.0.1", 5000),
        ) as tunnel:
            
            api_url = f"http://127.0.0.1:{tunnel.local_bind_port}/generate"
            print(f"Tunnel SSH ouvert")

            with open(fichier_obj, "rb") as f:
                files = {"file": f}
                data = {"prompt": prompt, "negative_prompt": negative_prompt, "prompt_wrapper": prompt_wrapper, "steps": steps, "guidance": guidance,"HF_TOKEN":HF_TOKEN}
                response = requests.post(api_url, files=files, data=data)

            if response.status_code == 200:
                zip_path = Path(output_dir) / "resultat_texture.zip"
                with open(zip_path, "wb") as f:
                    f.write(response.content)
                print("Zip reçu !")
            else:
                print(f"Erreur API : {response.text}")
                return None, []
                
            extract_dir = "extracted_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            extract_path = Path(output_dir) / extract_dir
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_path)
                
            full_mesh_dir_path = extract_path.resolve()
            
            abs_mesh_path = None
            files_in_mesh = []
            
            if full_mesh_dir_path.exists():
                abs_mesh_path = full_mesh_dir_path
                files_in_mesh = list(full_mesh_dir_path.iterdir())
                print("Fichiers extraits (Chemins complets) :", files_in_mesh)
            else:
                print(f"Le dossier n'existe pas : {full_mesh_dir_path}")

        return abs_mesh_path, files_in_mesh

    except Exception as e:
        print(f"SSH Error : {e}")
        return None, []