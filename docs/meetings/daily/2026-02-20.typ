#import "./template.typ": meeting, attendees, team

#show: meeting.with(
  date: datetime(year: 2026, month: 2, day: 20)
)

#attendees()

*Location*: 23N406 | *Time*: 9h00 | *Scribe* : Louis

- M:
  - Hier: création texture canard, recherche $->$ trouvé un repo GitHub + démo huggingface, testé mais pas parfait
  - Ajd: TBD
  - Remarques: comment évaluer les différentes solutions
- A:
  - Hier: trouvé comment modifier un modèle importé, premiers designs de supports, discuté avec Jérôme $->$ possibilité de faire des découpes sur bois pour des choses plus grandes
  - Ajd: réflexion sur l'environnement général, à discuter avec la team robot
- PY / N:
  - Hier: librairies ok, mouvements ok (MoveJ $A -> B$), que 1h à disposition $->$ pas pu tout tester
  - Ajd: continuer tests simulateur mais pas sur bras avant lundi
  - Remarques: processus de test assez lent car test sur simulateur obligatoire, créé un wrapper pour faciliter la traduction simulateur $->$ bras
- C:
  - Hier: complété tuto
  - Ajd: continuer tuto
  - Remarques: pipeline de calibration difficile à mettre en place sans accès au robot, caméra faite pour le software
- K:
  - Hier: testé différentes solutions de génération de textures, demande accès à Disco/Cha-Cha
  - Ajd: discussion avec Marco $->$ choix solution
  - Remarques: mémoire limitée sur Calypso, modèle assez demandant
- J:
  - Hier: recherche génération textures $->$ TEXTure, admin
  - Ajd: sélection/validation de la solution
- L:
  - Hier: algorithme, setup docker pour TEXTure
  - Ajd: peut-être commencer implémentation de l'algo, admin
  - Remarques: peut-être un peu de prompt engineering nécessaire pour avoir un bon résultat

#line(length: 100%)

- A: réunion avec CTO et PO $=>$ probablement quelques tâches administrative et/ou modifications
- C: milestones de la semaine prochaine à mettre dans la présentation
- PY: refaire schéma
- A: pensez au portfolio
- K: portfolio le matin ? ou l'après-midi ?
- L: retrospective en fin d'après-midi $->$ *15h00*
- L: repo team robot ?
- PY: repo/fork perso
- L: si possible mettre, dans l'organisation
- PY: documentation centralisée? $->$ oui
- J: vérifier si une branche existe déjà avant d'en créer une (p.ex. `doc/meetings`)