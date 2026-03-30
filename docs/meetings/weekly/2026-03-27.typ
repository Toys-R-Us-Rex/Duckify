#import "./template.typ": meeting, milestone-part, milestone-parts

#show: meeting.with(
  date: datetime(year: 2026, month: 3, day: 27),
  location: [23N418],
  time: [08h15],
  scribe: "C"
)

= Milestones

*Marco*: Présentation de la milestone hebdomadaire

  - Réussi:
    - Pipeline complet opérationnel
    - Dessin d’images générées par IA
    - Gestion de multiples couleurs avec changements automatiques
  - En attente:
    - Pipeline avec interface utilisateur
    - Site web promotionnel

= GenAI

*Marco*: Introduction du milestone du groupe

*Alexandre*:
  - Rejoint la team GenAI pour approfondir le prompt engineering
    - Ajout de contexte
    - Tests de prompts courts et longs
    - Focus sur des prompts orientés jeux vidéo
  - Génération d’images:
    - Animaux
    - Jeux vidéo (Link, Mario): manque d’éléments distinctifs → possible problème de coPierre-Yvesright ou de données d’entraînement
    - Manga (Sharingan Naruto): mêmes limitations observées
  - Conclusion:
    - Difficultés à obtenir un bon résultat selon l’univers demandé
    - *Lettru*: Tests supplémentaires ? Est-ce réellement la cause ?
      - Pas de temps disponible pour approfondir
    - *Travelleto* (à la team GenAI): tests automatiques ?
      - Réutilisation possible du travail de *Marco*
      - Intégration envisageable dans le process
      - Pas de temps pour la mise en place

*Marco*:
  - Création d’un exemple démontrant la faisabilité
    - Space hors-service (pause)
    - Mise en place du dispositif en local sur Disco "->" pas de limite de crédits
    - Création d’un dataset pour le fine-tuning
  - *Lettru*: Pourquoi ne pas avoir travaillé en local plus tôt ?
    - Réponse: la mise en local répond au dérangement du site oneline (Space)

*Kevin*:
  - Présentation de FreeU: outil d’amélioration de la qualité globale d’images générées
    - Fonctionnement:
      - Deux facteurs pour le lissage et la restauration de texture
    - Démonstration:
      - Comparaison avec/sans FreeU sur mêmes prompts/seeds
      - 10 générations de Batman avec seeds différentes
  - *Travelleto*: Problème d’yeux décalés
    - *Lettru*: Problème d’alignement ?
  - Conclusion:
    - Texture nettement améliorée avec FreeU
    - Continuer avec les valeurs recommandées
    - Essais de fine-tuning prévus

*Lettru* à *Marco*:
  - Est-ce image2texture ?
  - Réponse: Utilisé pour l’entraînement
  - Intégration dans le pipeline actuel ?

= Tracing

*Jeremy*:
  - Focus sur la génération de tests pour la team robot
  - Nouvelle UV map:
    - Séparation des zones pour éviter la superposition de pixels
    - Redesign du masque des zones non dessinables
  - Réduction du nombre de points sur les traces (demande team robot)
    - Il faudrai affiné les contours pour réduire le nombre de points
    - Risque de superposition de couleurs
    - Erreurs dans la création des formes "->" résolues via une librairie externe
    - *Lettru*: Comment obtenir un résultat vraiment ressemblant ?
      - Utilisation d’une fonction de réduction de points faisant partie de la librarie actuel
      - Suffisant avec la taille du feutre
      - *Pierre-Yves*: Idée: supprimer les points trop proches
    - *Lettru*: Problème de palettisation ?

= 3D Printing

*Alexandre*:
  - Possibilité d’utiliser 8 couleurs (minus le jaune déjà présent sur le canard)
  - Deux supports "->" tests parallélisables
  - Le robot peut soulever le canard
    - Pas d’observation critique
    - *Cédric*: Goupille imprimée en 3D ?
    - *Louis*: Scotch double face ?

= Robot

*Louis*:
  - Aide demandé par *Pierre-Yves*
  - Objectif: déterminer la position optimale du support
    - Méthode:
      - Points aléatoires sur le canard
      - Position aléatoire du support
      - Test d’accessibilité via le code robot
    - Résultats:
      - Graphe validant l’intuition sur le plan XY
      - Meilleure accessibilité si support plus bas en Z
      - *Lettru*: Pourquoi seulement la moitié du canard ?
        - On dessine une face à la fois
      - *Lettru*: Testé avec plus de points ?
        - Faisable, relance simple
      - *Alexandre*: Problème si le canard est centré
        - Possibilité de déplacer les racks de feutres
    - Zones difficiles:
      - Arrière de la tête
      - Sous le bec
      - Queue
      - Avant/arrière: difficiles mais pas impossibles
    - Conclusion:
      - Résultats cohérents avec l’intuition
      - *Lettru*: Position optimale ?
        - Pas nécessaire d’être exact

*Nathan*:
  - Intégration robot
    - Simulation via Docker
    - Transfert du code sans difficulté majeure
    - Problèmes de dépendances Pierre-YvesBullet
      - Pierre-Yvesthon 3.13 "->" retour à 3.11
      - Compatibilité variable selon machine
  - Conclusion:
    - Fonctionne bien sous Linux
    - Windows nécessite des build tools
  - *Lettru*: Docker inclut-il ces outils ?
    - Docker uniquement pour la simulation
    - Dockerisation complète du projet à évaluer

*Pierre-Yves*:
  - Présentation de l’objectif de la team robot
  - Vidéo: dessin de 3 traits de couleurs différentes
    - Changement de stylo automatisé
    - Suivi du chemin
  - Temps de calcul:
    - Formes simples: correct
    - Images IA complexes (tatouages tribaux): long
      - *Lettru*: Pourquoi ?
        - Beaucoup de points et artefacts
  - Temps de déplacement:
    - Dépend du nombre de points générés par le planner
  - Switch pendant le dessin:
    - Pas de test de collision
    - Problème à résoudre
    - Dernier joint = rotation du stylo mais pas bloquant

= Intégration

*Louis*:
  - Tracing "->" entièrement intégré
  - GenAI "->" en attente de validation PR
  - Robot "->" bloqué par l’intégration de ur3e-control

= Website

*Alexandre*:
  - Présentation d’une ébauche du site promotionnel
    - Design majoritairement généré via “Bolt”
    - Description du projet
    - Fiches simples sur les groupes (GenAI, Tracing, Robot, 3D Print)
    - Preview des canards (1 pour l’instant)
    - Vidéos du robot en action

*Lettru*: Pour le client, il manque:
  - Une expérience utilisateur complète
  Idée du l'équipe:
    - Entrée d’un prompt "->" génération d’un canard
    - Démonstration interactive

= Prochaine semaine

Préparation de la présentation au CEO

*Pierre-Yves*, *Cédric*, *Jeremy*:
  - Correction de la partie dessin
  - Tracing: réduire ou optimiser les points
  - Ajustement de la pression du stylo
  - Calibration/tests intermédiaires lors du changement de stylo

*Marco*:
  - Fine-tuning
  - Intégration benchmark
  - Organisation administrative

*Nathan*:
  - Intégration code robot
  - Dockerisation du projet
  - Support UI

*Alexandre*:
  - Site promotionnel
  - Recherche d’un stylo plus fin
    - Nouveau support ?

*Kevin*:
  - PR GenAI
  - PR Docker
  - Support tracing

*Louis*:
  - Intégration
  - GenTexture "->" Tracing
