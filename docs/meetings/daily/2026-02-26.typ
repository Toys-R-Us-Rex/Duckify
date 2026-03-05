#import "./template.typ": *

#show: meeting.with(
  date: datetime(year: 2026, month: 2, day: 26),
  location: [23N316],
  time: [9h00],
  absent: ("A",),
  scribe: "C"
)

*Alex* :
- Support à feutre validé et imprimé, l'intégration ne sera normalement pas un problème
- Réunion fixée pour découpe laser
- Toujours du travail à faire pour le support du canard
  - Design
  - Taille
ajd :
- Révision de la plaque en bois pour fabrication
 - Passer d'un assemblage creuser à un assemblage par des goupille
 - Déterminer la position idéale pour principalement le support du canard et les supports à stylo
- Poursuivre le design du support (avoir une version validée + imprimée pour la review de la semaine semble complexe)

*Nathan*: 
- Algo pour permettre au robot de prendre et posé un stylo dans un Notebook
- Difficulté à calculer les collisions de tout l'espace de travail avec les objets
  - Change pour un fonction qui retournera si le point est atteignable depuis la position actuel
ajd:
  - Test de fonction crée + sur robot

*Cédric*: 
- Correction de la formule pour la calibration TCP
- Possibilité de passer des coordonnées relatives à l'objet aux coordonnées TCP pour robot
ajd:
- Tester sur le robot
- Intégration de la calibration dans le pipeline
- Code pour dessiné plusieurs ligne/forme en un calibration

*Jeremy*:
- Validation pipeline tracing
ajd:
- test pipeline complet
- PV réunion avec CEO

*Louis*:
- P-Y + Kevin: définir la partie intégration du projet
  - Notebook pour setup intégration
- Implémenter transformation coordonnée texture sur objet
  - Contrainte UV mapping
- Review de Pull-Request
ajd:
- Finaliser pull request resampling
- Finaliser exportation donnée avec team robot
- Resampling contour sur 3D avec Jeremy


*Kevin*:
- Tester 6 solutions
  - Disco avec slurm
  - Trop long sans disco
- Réunion pour intégration avec P-Y et Louis
adj:
- Commencer structure de classes basiques d’intégration avec la pipeline globale afin d’accueillir la solution IA choisie
- Continuer de chercher des solutions avec calypso comme serveur

*Marco*:
- Test possible solution image2texture
- Mise en place du Benchmark
- Recherche pour la présentation (text2texture, image2texture)
#blocker:
  - Pas de validation du modèle de canard
adj:
- Ajout d'images dans GitHub
- Création d'un container
- Décision pour un model (text2texture, image2texture)


*P-Y*:
- meeting intégration
- Kevin + Jeremy: défine model pour 1ère intégration
- _Discussion avec groupe robot_:
  - Dessin sur surface plan incliné
  - Plan, multiligne
- Discussion tracing pour le domaine du robot
- Utilisation de Trimesh pour les collisions
  - Simple algo pour évité les collisions (convexe)
adj:
- Test avec le robot
  - finir le pipeline d’intégration (simple test)

Remarques:
 - Jeremy: manque de communication dans l'équipe robot
 - Réunion avec CEO:
  - Manque d'organisation pour la réunion
  - Les Slides n'étaient pas pertinente pour le CEO
 - Louis: Gestion des tâches sur JIRA a actualisé
  - _Team robot_: impression tâches déjà complétée?
 - Alex : Pour l'instant, il n'est pas possible d'avoir de position fixe (se baser sur la position d'éléments pour dessiner donc) : Comment allez-vous vous y prendre ?
  - Possibilité d'utilisé la position relative -> Transformation des cordonnées sur objet à cordonnées robot TCP.

Décision:
- Utiliser Calypso pour la génération de texture, plus Disco
- 14h30: 1ère version du pipeline prêt à être testé
  - Pipeline complet
  - Dessiner sur deux faces d'un trapèze
- Organisation: idée désignation de responsable pour les présentations

