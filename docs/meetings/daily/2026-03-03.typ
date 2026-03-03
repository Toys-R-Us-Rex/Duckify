#import "./template.typ": *

#show: meeting.with(
  date: datetime(year: 2026, month: 3, day: 3),
  location: [23N316],
  time: [9h00],
  scribe: "J"
)

*Louis*

- Setup workflow pour compiler la doc
- Commencé a setup un docker pour MV-Adapter $->$ quelques problèmes avec une dépendance
- ajd:
  - Finir docker pour MV-Adapter

*Jeremy*
- hier:
  - Improvement : détecter des patchs de couleur à l'intérieur de patch de couleur

- ajd:
  - Continuer le développement de cette improvement

- Remarque: le pipeline reste à tester par la team robot

*Marco*
- hier:
  - mise en place d'un benchmark 
  - démonstration de résultats
- ajd:
  - automatisation du benchmark
  
*Kevin*
- hier:
  - répondu aux commentaires d'une pool request, en attente de retour de Louis
  - Préparation de slides pour meeting avec CEO
- ajd: 
  - continuer les recherches de solution


*Alexandre*
- hier:
  - modélisation 3d : modifications du support, préparation de modèle pour choix CEO
  - impression du support, du canard
  - recherche des mesures idéales pour impression (limites atteintes)
- ajd:
  - modification du support par rapport aux feutres (à choisir) - optimisation à voir
  - a dispo du groupe robot
- Remarque: 
  - commencer à décider du nombre de couleurs

*Cédric*
- hier:
  - diagrammes UML
  - Transformation points real-world -> points simulation
- ajd:
  - Poursuite du travail sur le pipeline robot

*Nathan*
- hier: 
  - Implémentation du nouveau pipeline : function get_reachable()
- ajd:
  - CEO's meeting + implémentation

*Pierre-Yves*
- hier: 
  - Implémentation du nouveau pipeline : collision / reformat path_finding
- ajd:
  - 2h de tests cette après-midi - serait optimale d'y être à 4 personnes