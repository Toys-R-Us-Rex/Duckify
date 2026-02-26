import requests
from sshtunnel import SSHTunnelForwarder

SSH_HOST = '192.168.91.15'
SSH_USER = 'root'
SSH_KEY_PATH = '~/.ssh/wireguard'  


FICHIER_OBJ = "./models/mesh.obj"  
PROMPT = "A blue duck with a red nose"

print("Connexion SSH...")
try:
    with SSHTunnelForwarder(
        (SSH_HOST, 22),
        ssh_username=SSH_USER,
        ssh_pkey=SSH_KEY_PATH,
        remote_bind_address=('127.0.0.1', 5000) 
    ) as tunnel:
        
        api_url = f'http://127.0.0.1:{tunnel.local_bind_port}/generate'
        print(f"Tunnel ouvert. Envoi de la requête vers {api_url}...")

        # Préparation des fichiers
        files = {'file': open(FICHIER_OBJ, 'rb')}
        data = {'prompt': PROMPT}

        response = requests.post(api_url, files=files, data=data)

        if response.status_code == 200:
            print("Succès ! Téléchargement du ZIP...")
            with open('resultat_texture.zip', 'wb') as f:
                f.write(response.content)
            print(" Fichier 'resultat_texture.zip' reçu !")
        else:
            print(f" Erreur : {response.text}")

except Exception as e:
    print(f"Erreur globale : {e}")