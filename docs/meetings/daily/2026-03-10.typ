#import "./template.typ": *

#show: meeting.with(
  date: datetime(year: 2026, month: 3, day: 10),
  location: [23N314],
  time: [9h00],
  scribe: "N",
)

*Alex*:
- Mise en place + démarrage déplacement de stylo
- Setup environnement
- Imprimer support avec points de calibration
  - Peut réimprimer
- Mise à jour de documentation impression
- Nouveau Stylo
- Envoyer une nouvelle commande de goupille à Mme Richard

*Marco*:
- on premise solution image to texture
  - Modèle de diffusion local avec GPU Disco (plus GPT)
- Protocole de test
  - Hyper-paramètres configurable
- Choix image2texture ou text2texture pas encore sûre
- Comparaison des modèles avec benchmark et prompt similaire

*Kevin*:
- Génération avec prompts
- Comparaison des modèles avec benchmark et prompt similaire

*Louis*:
- Docker image MV Adapter "fonctionne"
  - PR à valider
- Export des axes (tracing) + documentation
- Contours Polygones

*Jeremy*:
- Réduction couleurs des images -> couleurs des stylos

*PY*:
- PyBullet: simulation des collisions
- Intégrer le canard et les traces dans la simulation

*Nathan*:
- Hier:
  - Intégration du canard dans la simulation + doc
  - Aidé Alex avec le simulateur
- Ajd:
  - Comprendre PyBullet
  - Fichiers 3D de collisions (table + environnement)

*Cédric*:
- Documentation UML calibration et docstring
- Comprendre code PyBullet et continuer documentation
- Voir la pression et la force du bras avec le stylo
  - Comprendre le signal de sortie du robot


== Are the teams on track (personal opinion) ?

*GenAI*
- Oui

*Tracing*
- Oui

*Robot*
- Oui

*Impression 3D*
- Pas sûre
  - Trouver une solution pour le support