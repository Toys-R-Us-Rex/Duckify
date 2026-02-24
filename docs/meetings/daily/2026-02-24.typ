#import "./template.typ": meeting, attendees, team, blocker

#show: meeting.with(
  date: datetime(year: 2026, month: 2, day: 24),
  absent: ("K",),
  extra: ([L. Lettry],),
  location: [23N316],
  time: [9h00],
  scribe: "PY"
)

*Louis*:

*Marco*: 
Parle de sa rétrospective. 
Il a plan plusieurs modèles de canards
Uniquement avec textures
Un modèle, une UV map -> pour créer différentes textures
But: faire plusieurs itérations, et ensuite un benchmark. Afin de pouvoir tester
différentes modèles et évaluer le meilleur. 
Objectif: pour la présentation: avoir obtenu le bon modèle.

D'ici demain, la team LLM peut se dispatcher.
Q (Louis): tourne sur Calypso
M: oui, entre 5 et 10 minutes
J: Test monochrome ?
M: Montre un exemple tricolore, rouge bleu bleu ( VScode. MP4 )
-> possibilité d'avoir des prompts

*Louis*: 
Avec *Jeremy* : peer programming pour faire les fonctions de l algo de tracing.
Aujourd'hui travail en parallèle. Normalement fini pour ce soir le gros du pipeline. Git LFS : pour les textures. 
- Configuration Jira pour les pull requests ( ID de la task ).
PY: quand est la présentation LLM ?
Louis: ce soir ou demain ?

*Alex*: Disposition des pièces générales
base en bois puis découpe laser. 
- monter la plaque qui soutient le robot. Pas certains sur la mesure du trou 1. 
A définir: la hauteur idéale du soutient robot
Pour l'assemblage:
- pièces en noir = robot simplified ( 170 mm )
- 4 supports pour les 4 couleurs ( pour l'instant )
- dessous , modeling de la plaque ( en métal )

Montre une photo: Vision intérieure des supports qui épouse la forme du feutre
on part sur une seule solution qui s'adapte. Le design est fini pour aujourd'hui -> présentation demain
Q ( Jeremy ): prêt pour la présentation de fin de semaine ?
L: 
C: Support pour les crayons , simple, Sur le cote
Aussi semble un peu trop proche du robot selon le schéma?
Bonne forme générale
A: Problème qu'on va rencontrer : 600 x 300 taille idéale. ( on est a 360 )
Propositions: 1) plusieurs pièces 2)
C: il ne s'attendait pas a ça: plutôt une plaque avec les trous déjà faits
L: on n'a pas besoin d'une position absolue qui est statique.
A: Pour l'instant plus de largesse / flexibilité
J: Pour le support du canard: quelque chose qui s'enlève.
C: 3 piques ?
D: on met / finalise les supports avant la calibration. 

*Cedric* 

On va aller tester cet après midi. PY: on a la confirmation officielle

*Nathan*
On doit quand même savoir exactement ou mettre le canard, pour savoir si le bras a la reach nécessaire pour le peindre
Va montrer les captures d'écran:
- A fait un document , qui liste les points dans l'espace 3d accessibles par le bras
- visualisation: en vert , le domaine accessible
- Objectif: arrive a atteindre la surface du canard sans rentrer en collision
J: il faut faire valider en amont.


*PY*:
par rapport aux collisions, pour le dessin 2D, restrictions plus simples définies sur le range des joints

- J: Généralisable en 3D ?
- PY: Pour l instant , façon simple , mais pas transposable en 3D

L: demande de meeting, par exemple le jeudi, avec Monsieur Lettru ? 
Lettru: Il faut lui écrire, pour demander ses disponibilités
L: tres important avant de continuer le projet ( dans un mauvais direction ? ), d'obtenir son approbation. 

J: plus de problème d'accès au labo ?
PY: pour cette semaine aucun soucis. 

Lettru: le mail doit être simple:
"Bonjour on souhaite vous voir pour telle date ? si c'est disponible oui, sinon quelles sont vos disponibilités ?"





*Rétrospective sur le daily meeting*
*Lettru*: Qu'est ce que vous en pensez ? 
C: le but c'est d informer sur son avancée ET de pouvoir rectifier si quelqu'un voit qu'un autre groupe.
PY: mieux que d'habitude car on peut voir

Alex: est ce que la taille vous convient ?
PY: 2x ?
Alex: pas sur, a vérifier ? #blocker

Lettru: utiliser le daily fin de discuter des éléments qui bloquent ? ( exemple: taille du canard)

le retour: peut être trop chronologique ?

*Lettru*: Vrai objectif du daily: "Suis-je a l'heure ? "

Il manque une personne chef de projet 
-> contact plus direct avec le clients pour TOUTES les informations manquantes.

ex: comment "manipuler le client" pour obtenir la conclusion désirée ?

Lettru: Cela Aurait du être fait plus tôt !

Combiner: équipe tracing -> équipe robot. ( intégration d’éléments )

Q1: Comment avoir le plus d'informations sur ce qui marche ou ce qui ne marche pas ? 
Q2: Est ce que, ce que le dev X est en train de faire est utile ou non ( a ce point du projet )

Solution: Il faut un chef de projet qui tranche. 


Comment doit être un "bon" daily meeting ?  Oser dire quand quelqu'un se trompe et demander aux personnes concernées d'en rediscuter et même de refaire. 


Si "ce que je devais faire , est ce accompli ? " -> oui / non -> pourquoi ?









Retour portfolios:

- Prendre ce qu'on a fait, et dire : tel jour j'ai eu tel problème, et j'ai fait tel report et je l'ai résolu de cette manière ( preuve )
- Ne doit PAS être un journal

- Doit résumer les *contributions*

- Exemple: J'ai amélioré ma communication

- Attention au liens morts

- "j'ai fait des recherches" -> Elles sont la "lien"

- Document, n'est pas forcement une bonne démonstration de communication

- Dans l'ensemble, c'est plutôt pas mal

- Quand même faire un effort sur la structure?

- Les questions d'entretien: Ne peut pas demander des questions ultra spécifiques des le début. Il faut une ligne directrice, et des questions plus "vagues"
--> "Si vous avez quelque chose dont vous aimeriez me parler, qu'est ce que c'est"
--> "Quelle est la chose la plus difficile que vous ayez fait ? "
--> "Si vous êtes bloques lors d une implémentation, quelle est la procédure pour la résoudre ? "






