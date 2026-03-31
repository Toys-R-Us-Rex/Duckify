#import "./template.typ": *

#show: meeting.with(
  date: datetime(year: 2026, month: 3, day: 30),
  location: [23N316 / Online],
  time: [8h15],
  scribe: "L",
  absent: "K"
)

*Marco*
- Ce WE:
  - testé le fine-tuning avec les modèles 3D + 6 vues
  - 1ère itération $->$ dumb-down le modèle, problème de couleurs
  - 2ème itération $->$ pas bcp de changement, pas bcp de signal positif
  - éventuellement tester l'augmentation de données (actuellement ~30 d'inputs)
- L: Temps ?
- M: ~60 epochs = ~30 min
- Ajd
  - 1-2h de fine-tuning, plus de données
  - intégration du benchmark avec Kevin
  - #blocker: serveur sur le user de Kevin
- A: data augmentation, si ça marche, est-ce intégrable dans le temps imparti ?
- M: oui, dans la config, il suffit de changer "poids intégrés" $->$ "poids custom"
- A: possible de tester autre chose que la data augmentation ?
- M: un peu la seule chose possible dans le temps à disposition

*Jeremy*
- Vendredi
  - Pouvoir exclure plusieurs couleurs de la palettization
  - Participation aux tests avec la team robot
- Ajd
  - Finir ce qui a été commencé vendredi
  - configurer la taille du stylo
  - Traces complètes pour la démo

*Alexandre*
- Vendredi
  - Impression de l'adaptateur pour feutre
  - A fini le rapport GenAI
- Pas encore de réponse de M. Darbellay pour filmer une impression
- Ajd
  - Continuer le site de promotion: clarifier le contenu
  - Si les nouveaux feutres sont mieux $->$ éventuellement achat de feutres supplémentaires
- M: éventuellement mercredi après-midi, peut aider pour la vidéo (montage, etc.)

*Louis*
- Vendredi 
  - Intégration robot dans l'interface
  - Regarder avec Cédric pour un merge de branche
  - Labo avec P-Y
  - Robot : utiliser force ?
- Auj
  - Poursuite de la partie robot dans l'interface
  - #blocker Si Kevin valide la PR, GenAI intégrée

*Pierre-Yves*
- Vendredi
  - Tests au labo:
    - Test avec l'ordi de Louis
    - Fait fonctionner la lecture des forces
    - Visite de Lettry, très enthousiaste $->$ être ambitieux et tester des choses
- Utiliser les forces
- Corriger la calibration et la transformation $->$ p.ex. avec ICP (nuage de points) pour augmenter la précision
- Ce WE
  - beaucoup de changements
  - nettoyage du dead-code de pathfing
  - essai d'amélioration du smoothing
  - montre les nouveaux plots: encore quelques pics mais nette amélioration
- Ajd
  - utiliser les traces pour faire des vrais dessins
  - intégrer le flip du canard dans le pipeline (rotation des traces au milieu)
  - tester ICP et voir si amélioration de la précision
  - quelques corrections des angles
- J: timing pour le robot ?
- PY: pour moi, le plus possible: ce matin, cet après-midi, demain, ...
- J: quelles contraintes ?
- PY: utilisation par d'autres personnes

*Cédric*
- Vendredi
  - Tests au labo
  - Logs des forces: ok, à analyser
  - Quelques corrections du code
- Ajd
  - Regarder avec Louis pour merge dans main
  - Filtre pour avoir les coordonnées dans le bon sens quand on tourne le canard
  - Analyser et intégrer les forces
  - Labo + debugging

*Nathan*
- Vendredi
  - Containerization du pipeline
  - Docker compose pour tout lancer $->$ à tester si chaque partie fonctionne correctement
  - Docker compose pour lancer Gazebo en même temps
  - À faire: tester la communication avec Gazebo
- Ajd
  - Tester et vérifier, avec 1 personne de chaque groupe

*Commentaires*
- *Alex* à la team robot: testez les nouveaux feutres, pour savoir s'il faut aller en chercher d'autres
- *Pierre-Yves*: d'autres priorités, p.ex. précision de la calibration
- *Alex* à *Marco*: possible de fournir les meilleurs modèles pour mettre sur le site ?
- *Pierre-Yves*: traces dessinables pour les textures de démo ?
  - *Jeremy*: Pas encore tracées, mais normalement dans la matinée c'est bon
- *Louis* possible de rajouter un offset manuel ?
  - *Cédric* rotation z oui, pas encore pour la position
