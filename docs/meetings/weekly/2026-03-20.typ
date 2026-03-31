#import "./template.typ": meeting, milestone-part, milestone-parts

#show: meeting.with(
  date: datetime(year: 2026, month: 3, day: 20),
  absent: ("PO",),
  location: [23N225],
  time: [13h00],
  scribe: "PY"
)


== Milestones

- Pas pu réaliser tout ce qu on voulait , par manque de temps


= GenAI

- pipeline est intégré, mais manque de temps. Pense que ce sera fini pour la semaine prochaine. Notamment la review de la pull request.

- Detail du benchmarking. Reprise du travail de semaine 2, avec automatisation du benchmark. Ce qu'il manque: un filtre qui trouve instantanément le meilleur canard.


- Les scripts: 

  + appelle text2texture pour faire de la valorisation de données

  + prends les données et les placent sur Excel
- JSON avec résultat du benchmark -> export sur Excel

( montre le pwp ) Le benchmark humain est a droit.

Avec le même prompte il y a encore de la variation. 
Les notes sont rajoutées a la main


- Prochaine etape: evaluer de maniere "automatisee"

-> input une image , en output, le score. 

Difficile de juger pour le moment si le robot est capable de dessiner l'image. 

Types de canards dessines: 4 professions. ( sans contrainte de couleurs )

Lettru: essai astronaute ? gap entre ce qui semble être attendu ( prompt vague ) est ce que Marco a montre ( prompt précis )

* Revues des canards: *

- Image duck minecraft = Creeper ?!: Lettru ( difficile a juger si le resultat est correct)

- Image duck Pikachu: -> ok joues rouges

- Image duck super mario: -> pas évident

- Image duck chevalier: -> evident

Lettru: peut etre utiliser un "rubber duck avec element X " pourrait ameliorer le resultat, au lieu de dire " donald duck "

-> Ceux qui fonctionnnent le mieux : Spiderman, batman, 
 
Proposition: limiter les prompts par sécurité ( NSFW ect.)

* Pipeline: *

(cf schema)

client.py -> server.py -> mv_adapter ( and back)



== Tracing

Liste des issues:
- petites artifacts       W         -> couleur par couleur
- zones non atteignables  W         -> mask de zones
- remplissage             W         -> points trop alignes
- dataset de traces       W         -> dataset incrémental
- cross UV islands        L         -> décaler les points


visuellemnet (construction worker) -> W
petits bugs -> traits non dessines

temps de calcul: 7 min 30

== 3D Printing

milestones:

- Fixer l'effet de friction           -> W
- Ajouter un ressort pour le gripper  -> W
- Stabilité du support canard         -> L

Designer du support du feutre ( le ressort va dedans )

Conclusion -> le test est fonctionnel ( video )

Q: Reprendre un stylo qu'on vient de poser , un problème ?
R: Non position comme au début déjà un peu penché

L’intégration n'est pas encore réalisée, mais la module de prise de stylo est déjà fonctionnel.


== Robot 

- Correction safety PyBullet : no/partially
- Draw on 3d surface : yes
- Draw with 2 pens : no

=== Path finding optimisation 

Graph detectant pleins de piques qui font beaucoup bouger le robot => à reussi à smoother la courbe mais problèmes de transitions (2 piques 1 au debut et 1 à la fin)


=== Dessin d'un cercle sur le canard

Prend du temps pour dessiner ce cercle (35s)
Vitesse du robot limité (pour la phase de test) , la vitesse est / 2


=== Robot pipeline

Tout est bon sauf : 

- Filtrage face gauche et droite + intégration a voir et faire 
- Pathfinding : Problèmes de transition (fin d'une trace à une nouvelle trace)
- Intégration du gripper à ajouter

_Semaine prochaine : Normalement résolu cela_ 

#pagebreak()
= User Inteface

Objectif: avoir un outil qui peut
- configurer
- exécuter
- voir
-> toutes les étapes du pipeline. 

UI fait avec pyQT.

Peut lister les textures, et les visualiser, avec plein d'options ( remplissage ect )

[demo live sur pyQT] exemple de choix de palette et temsp de calcul.

En cours: Intégration des parties calibration et calibration dans PyQT 

Q: Ajout de couleur a ignorer ?
R: Pas important mais peut être rajoute 

Q: ( Lettry): Est ce que c'est le choix final d'UI pour le client
R: Possible oui

but : tout faire pour convaincre le client. Il faut gérer le temps d'attente ( computation ect. )

Idee: reprendre les images, comme summer school 2. 

=> MARKETING <=

= Marketing prochaine semaine

- Présentation ? Lettry -> vidéo de présentation pour vendre le produit au client.

but : tout faire pour convaincre le client. Il faut gérer le temps d'attente ( computation ect. )

Idée: reprendre les images, comme summer school 2.

= Amélioration GenAI

- Fine-tuning $->$ probablement pas un investissement judicieux, beaucoup de travail nécessaire
- Peut-être faire des recherches d'abord


= Répartition des devs

- rajouter du monde dans la team robot ( planner urgent )
- attendre avant de re-design le support

= Amélioration du lab

- protocole ultra précis pour le labo ( c'est très mauvais pour l'instant )

- organiser les sessions de robots en avance ( demande rapide )

- pour la génération d'image, suggestion de Lettry de re-entraîner / fine tuning 

-> "rubber duck"
-> controlnet ?

Pour Kevin V.






= Administratif

- évaluation le mercredi $->$ 30 minutes
- présentation au client le jeudi

== Conseils généraux
- Faire des objectifs plus long / détaillé

- Présentation au client $->$ probablement des conflits $->$ vendre du rêve et convaincre le client

#align(
  center,
  circle(
    align(center + horizon)[
      *Chef de projet*\
      #text(size: 2em)[*Marco*]
    ]
  )
)
