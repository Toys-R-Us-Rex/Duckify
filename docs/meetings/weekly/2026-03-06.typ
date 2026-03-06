#import "./template.typ": meeting, milestone-part, milestone-parts

#show: meeting.with(
  date: datetime(year: 2026, month: 3, day: 6),
  absent: ("PO",),
  location: [23N418],
  time: [10h00],
  scribe: "L"
)

= GenAI

== Milestones

- Benchmark: fait mais pas intégré
- Décider d'une solution: pas fait car encore des hallucinations
- Résultats prometteurs avec ChaCha et Disco

- Tracing (L): quantization de couleurs marche mieux avec du contraste, optimisations à faire mais pas encore pu tester parce qu'il fallait des résultats de la team GenAI
- NIMA (J): résultat entre 4 et 5 ? (M) soupçonne peut-être une gaussienne

== Commentaires

- #highlight[Inclure les conclusions !] Milestone acquis ou pas $->$ pourquoi ?
- Manque des informations sur le fonctionnement du système, p.ex. le fait que c'est non-déterministe, pourquoi plusieurs échantillons, etc.
- Pas forcément compréhensible pour quelqu'un d'externe à la team
- Étoile en dehors du canard ? Pourquoi ? Mieux expliciter ce que les images représentent
- Limitation des couleurs $->$ pas prendre des a priori sur les autres groupes, demander aux personnes concernées
- Communiquer sur les contraintes (p.ex. résolution minimum), maintenant / le plus tôt possible
- Mettre les prompts sous les images, montre aussi le progrès

= Tracing

- granularité ? vitesse vs. précision
- waypoints devrait ne pas s'arrêter

== Commentaires

- Présentation bien mais objectif: véhiculer de l'information
- Vaut la peine d'expliquer un peu comment les choses ont été faites $->$ aide à la compréhension, met en évidence les blockers / les questions
- Job du chef de projet, coordonner les équipes, s'assurer de la cohésion

= Robot

- Plus de point $=>$ plus la trajectoire est propre
- Retard à cause des vecteurs de rotation (pas Euler)
- Problèmes:
  - Compréhension mathématique
  - Temps avec le robot

== Milestones

- Conversion des coordonnées: ok
- Dessin sur surface plate mais pas avec un angle $->$ erreur de conversion (normale)

- Manipulation des outils $->$ dans la simulation ok mais pas testé
- Dessin sur le canard $->$ pas fait
- Dessin avec 2 stylos $->$ pas fait

*Semaine 4*
- Manipulation outils
- Dessin surface 3D
- Dessin avec plusieurs stylos
- Chercher et implémenter une solution de sécurité

== À faire

- Validation avec le robot
- Sécurité, 3 options
  + From scratch
  + Librairie externe
  + Movit2 $->$ lourde et complexe, mais liée à URBasic

= 3D

== Milestones

- Validations $->$ faites
- Supports: ok
- Pièces en bois: ok

*Semaine 4*

- Ajustements si nécessaire
- Alex $->$ team robot

= Conclusion

- Objectif principal: dessiner sur le canard en 3D
  - Pas atteint

- *Blockers*:
  - Changement de paradigme d'implémentation team robot
  - Contrainte de temps
  - GenAI $->$ pas de résultats utilisables intégrés

== Chef de projet
- Discuter avec chaque équipe pour l'intégration
- Intégrations réalisées en partie
- Se concentrer sur le pipeline complet, avec une implication des "chefs" de teams

== Commentaires
- quelques slides sur la gestion du projet
- intégration: définir les protocoles d'échanges entre teams
- chaque groupe doit pousser le milestone selon ses connaissance pour atteindre le but final, le chef de projet n'a pas forcément connaissance des difficultés ou objectifs précis


== Objectif
- Plusieurs stylos
- Sur le canard
  - Aile
  - Côté du cou
  - Arrière du cou
  - Endroit plus dur ?
- Définir les contraintes

#quote(block: true)[
  Using the #milestone-part[complete pipeline], draw #milestone-part[AI generated] shape #milestone-part[contours] with a #milestone-part[selected GenAI solution], on a #milestone-part[duck], installed on a #milestone-part[stable support], using #milestone-part[multiple colors], while #milestone-part[changing colors automatically]
]

#milestone-parts()

== Futures milestones:
- Collier autour du cou

#line(length: 100%)

- Inset de l'épaisseur du stylo

- (N) à quoi sert le benchmark ?
- (Lettry) très bonne question, important de remettre en question la légitimité du travail effectué
- (Lettry) Convaincre les autres / les décisions
- 

+ Forme géométrique à un endroit précis $->$ plutôt Image2Texture
+ Plus de créativité $->$ plutôt Text2Texture


== Meeting CEO
- liste de plus et de moins, de facteurs qui permettent de prendre une décision
- un peu timides, assumer les choix
- défendre le travail effectué, justifier
- #highlight[expliciter, pas de sous-entendus !]
- choix vs. décision

#quote(
  block: true,
  attribution: [L. Lettry]
)[Si on sait pas où on va, on arrive partout]

= Administratif

- tous les étudiants ISC + tous les profs
- présenter ce qu'on fait
- décalé dans 2 semaines
- mock evaluation la semaine prochaine (vendredi matin), 2 entretiens 20-30 minutes avec tout le monde

#align(
  center,
  {
    circle(
      align(center + horizon)[
        *Chef de projet*\
        #text(size: 2em)[*Jeremy*]
      ]
    )
  }
)
