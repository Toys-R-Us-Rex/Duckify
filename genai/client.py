import os
import requests
from sshtunnel import SSHTunnelForwarder
import zipfile
import datetime

SSH_HOST = '192.168.91.15'
SSH_USER = 'kevin.voisin'
SSH_KEY_PATH = os.path.expanduser('~/.ssh/wireguard_key')

def run(fichier_obj, prompt, base_path):
    print("Connexion SSH...")
    try:
        with SSHTunnelForwarder(
            (SSH_HOST, 22),
            ssh_username=SSH_USER,
            ssh_pkey=SSH_KEY_PATH,
            remote_bind_address=('127.0.0.1', 5000),
            ssh_timeout=10.0,
            banner_timeout=5.0
        ) as tunnel:
            
            api_url = f'http://127.0.0.1:{tunnel.local_bind_port}/generate'
            print(f"Tunnel ouvert. Envoi de la requête vers {api_url}...")

            file_path = os.path.join(base_path, fichier_obj)
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'prompt': prompt}
                response = requests.post(api_url, files=files, data=data)

            if response.status_code == 200:
                print("Succès ! Téléchargement du ZIP...")
                zip_path = os.path.join(base_path, 'resultat_texture.zip')
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                print("Fichier 'resultat_texture.zip' reçu !")
            else:
                print(f"Erreur API : {response.text}")
                return None, []
                
            # Dézipper le fichier
            extract_dir = 'extracted_' + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            extract_path = os.path.join(base_path, extract_dir)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
                
            mesh_dir = os.path.join(extract_path, 'experiment_api', 'mesh')
            full_mesh_dir_path = os.path.abspath(mesh_dir)
            print(f"Chemin complet vers le dossier mesh : {full_mesh_dir_path}")
            
            abs_mesh_path = None
            files_in_mesh = []
            
            if os.path.exists(full_mesh_dir_path):
                abs_mesh_path = full_mesh_dir_path
                files_in_mesh = [os.path.join(abs_mesh_path, f) for f in os.listdir(abs_mesh_path)]
                print("Fichiers extraits (Chemins complets) :", files_in_mesh)
            else:
                print(f"Le dossier n'existe pas : {full_mesh_dir_path}")

        return abs_mesh_path, files_in_mesh

    except Exception as e:
        print(f"Erreur globale SSH/Requête : {e}")
        return None, []