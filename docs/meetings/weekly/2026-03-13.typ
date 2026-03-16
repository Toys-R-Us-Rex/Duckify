#import "./template.typ": meeting, milestone-part, milestone-parts

#show: meeting.with(
  date: datetime(year: 2026, month: 3, day: 13),
  absent: (),
  location: [23N225],
  time: [13h00],
  scribe: "N"
)

= GenAI

- MV Adapter: OK

== Milestones

- Investiguer image2texture et text2texture

- Solution on prem
  - Flux Kontext 1 (Black Forest Labs) Text to image
  - SDXL (Stability.ai)

=== Image2Texture
- "Leakage" des textures
- Génération lente
- Solution pas suffisante

=== Text2Texture
- Problèmes d'orientation réglé
- Plus de variance, mais moins de leakage
- Génération plus rapide

== Commentaires

- Q: Génération plus rapide possible ?
  - R: 30 générations, 13 secondes par gén
- Q: Canard batman, spiderman, avec plus de sémantique, comment ça marche ?
  - R: A voir...


=== Image2Texture
Flux prend une image du model + prompt

=== Text2Texture
Benchmark: Prompt respecté ?

= Tracing

- Out-of-bounds problem
  - Calculate intersections with uv map edges

== Commentaires

- Q: Séparation possible les côtés du canard ?
  - R: Oui

- Q: UV Map améliorable ?
  - R: Pas de problèmes avec la UV map actuelle

= Robot

- Intégrer le code dans la repo Duckify
- Clean codebase


== Milestones

== À faire

= 3D

- Solution stabilité actuel est le skotch (pas encore testé)
  
== Milestones

- Correct the stability with scotch
  - Pas réussi, car pas encore testé
- Remove friction effect in pen support
  - Pas réussi, mais nouvelle solution imaginée
  - Possibilité de scotcher les support des stylos
  - Ressort dans le support ?

  
= Conclusion
- UI: Interface où on rentre un prompt qui utilise toute la pipeline
  - Vraiment nécessaire pour l'instant ?

- Robot:
  - Meilleure planification de l'unification du code.
  - Contrôle général: entre 2 traits ?
- Optimisation vitesse de dessin

== Chef de projet

== Commentaires

- Portfolios: "template" à venir
- Lancer startup

== Objectif
  - Partie intégration (avec interface ?)
  - Tester changement de stylo sur trapèze
  - Documenter les changements d'équipes au daily

= Administratif

#align(
  center,
  circle(
    align(center + horizon)[
      *Chef de projet*\
      #text(size: 2em)[*Kevin*]
    ]
  )
)
