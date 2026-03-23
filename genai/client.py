import datetime
import zipfile
from pathlib import Path
from typing import Optional

import requests
from sshtunnel import SSHTunnelForwarder


def generate_texture(obj_path: Path, prompt: str, output_dir: Path, negative_prompt: Optional[str] = None, prompt_wrapper: Optional[str] = None, steps: int = 30, guidance: float = 6.0, SSH_HOST: str = None, SSH_USER: str = None, SSH_KEY_PATH: str = None, HF_TOKEN: str = None) -> tuple[Optional[Path], list[Path]]:
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

            with open(obj_path, "rb") as f:
                files = {"file": f}
                data = {"prompt": prompt, "negative_prompt": negative_prompt, "prompt_wrapper": prompt_wrapper, "steps": steps, "guidance": guidance,"HF_TOKEN":HF_TOKEN}
                response = requests.post(api_url, files=files, data=data)

            if response.status_code == 200:
                zip_path = output_dir / "resultat_texture.zip"
                with open(zip_path, "wb") as f:
                    f.write(response.content)
                print("Zip reçu !")
            else:
                print(f"Erreur API : {response.text}")
                return None, []
                
            extract_dir = "extracted_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            extract_path = output_dir / extract_dir
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