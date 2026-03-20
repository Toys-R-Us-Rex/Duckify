#import "./template.typ": *

#show: meeting.with(
  date: datetime(year: 2026, month: 3, day: 17),
  location: [23N415],
  time: [9h00],
  scribe: "PY",
  absent: "K"
)

*Marco* : 

hier:
- a eu une discussion avec M.Lettry sur la génération d'image. Thème: comment avoir plus de données? Utilisation d'un script en python pour générer automatiquement sur Excel.
- exemple d'essais: Pikachu, Mrbeast, Fortnite ect
conclusion, pour les thèmes de JV c'est moins performant.

ajd:
- continue le benchmark humain / automatise


Q: est-ce pour toutes les images les mêmes seed ? A: elles sont aléatoires.


*Jeremy* :

hier:
- continue de résoudre des problèmes liées au remplissage de formes. Éviter que de trop petits artefacts soient visibles sur le canard.

exemple visuel:  
- segmentation et visualisation. Enlever les parties du canard que l'on ne garde pas. 

ajd:
- remplir des contour a l'aide de lignes 
- création de data classe en python



ajd:


*Louis* :

hier:
  - Résolution du problème des zones non atteignables ( comme le bord des yeux, dessous du canard,  intérieur du bord, dos du canard ). Fait manuellement sur Blender. 

  - amélioration de l'interface en pyQt, voir les traces, rotationable en 3D, visualisation contrôlable avec la souris. Possibilité de configurer la palette de couleur, et changer l'ordre d'utilisation des stylos ( par index de couleur ). 

Ajd: 
  - discuter de l'intégration
  - discuter de quels paramètres il faut configurer ( avec l'équipe robot)
  - un dataset de traces 


Alex: devons nous définir maintenant l'ordre des couleurs ? 
Réponse: pas nécessaire de choisir tous ensemble. Alex est l'expert il peut s'en charger

*Pierre-Yves* :

- Hier:
  - Restructuration des fonctions
  - Fichier PyBullet était mal organisé $->$ refactor en plusieurs fichiers
  - Regardé pour merge
  - Éléments bloquants $->$ résolu problème de "hover points"
- Ajd:
  - Changer l'ordre du pipeline (étapes de déplacement)

*Cédric* :
- hier:
  - préparation du pipeline,
  - A regardé le merge dev/merge-pipeline -> main
  - Nouvelle classe segment qui organise le pipeline de transformation trace -> tcp

*Nathan* : 
- hier:
  - A travaillé sur la nouvelle classe "segment"
  - A fait le filtre ( pour trier les traces sur le canards gauche vs droite )

- Ajd: finir le merge et la PR

*Alexandre* : 
- Hier : 
  - remanier la fonction de transition de stylos
  - impression d'un nouveau support ( échec avec le ressort )

- Auj : 
  - tester si la séquence ( changement de stylo ) fonctionne toujours bien
  - essayer de résoudre le problème du ressort

