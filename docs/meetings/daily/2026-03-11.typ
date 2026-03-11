#import "./template.typ": *

#show: meeting.with(
  date: datetime(year: 2026, month: 3, day: 11),
  location: [Online],
  time: [9h00],
  scribe: "A"
)

*Kevin*
Hier :
  - Choix des hyperparamètres avec marco (judicieux ?), seeds pas important à fixer
Auj :
  - Pareil

*Marco*
Hier :
  - Faire des générations de test -> objectif 80% du travail fait assez vite
Auj :
  - Continuité de hier

12 générations de calibration
Intérêt de changer la seed, fixe le nom d'inférence et on change la guidance

Pour 1 prompt : 10 générations avec changement de paramètre pour les 2 méthodes

K : demain soir, fini la présentation et pris une décision (reproduction de prompt, qualité)

M : protocole en ordre, benchmark pas de grande quantité donc score à la main

*Louis*
Hier :
- Vérifier les axes à l'export
- Corriger les axes du canard conformément à la discussion avec C
- Polygone de contours vérifié
- PRs en attente
Auj :
- avec J, finaliser les optimisations de tracing (flou artistique : micro pixel de différentes couleurs mélangés)

*Jeremy*
Hier :
- Continuer de mettre en place les optimisations/correction du pipeline de tracing lorsqu'une image générée est input.
Auj :
- Continuer et finaliser ce travail d'optimisation

*Cédric*
Hier :
- Simulation dessin sur le canard
- Investigation sur la force (pas encore de plot)
Auj :
- Poursuite de l'investigation sur les forces
- Test robot

*P-Y*
Hier :
- Intégration sur les collisions, self-collision, get_reachable 
Blocant(s) : 
- Problème de normal au niveau des yeux
- Essai de symbole infini : Pas tout est accessible, point manquant
- Normale qui varie de manière abrupt
Auj :
- Fixer les éléments bloquants
- Dessiner sur le canard

*Nathan*
Hier :
- Essai de PyBullet (Quickstart guide) pour aider la team
- Workspace dans blender pour tester les collisions
Auj :
- Continuer sur PyBullet

*Alex*:
Hier :
- Implémentation prototype code pour attraper et changer feutres (pas de mouvement entre le changement de feutre)
Auj :
- Test robot
- Feutre position calibration à voir -> C
