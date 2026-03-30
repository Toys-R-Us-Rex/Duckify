#import "./template.typ": *

#show: meeting.with(
  date: datetime(year: 2026, month: 3, day: 26),
  location: [23N316 / Online],
  time: [9h05],
  scribe: "M",
)

*Kevin*

Rétro:
  - Intégration de la pipeline GenAI avec Docker
  - Finetuning: Implémentation de la méthode Free Lunch U https://chenyangsi.top/FreeU/

Auj:
  - Finetuning: Continuer l'implémentation de la méthode Free Lunch U 

*Commentaire(s)*

L: Retour sur le prompt engineering ? Est-ce que wrapper le prompt améliore la génération. 

A: Rajouter précision donne peu d'amélioration

*Marco*

Rétro: 
- contact avec Lettry $->$ oui, faites du fine-tuning
- problématique: avoir des GLB de canards texturés $->$ solution trouvée sur Huggingface, contrainte de freemium $->$ répartir entre tous, chacun génère un canard par jour

Auj:
- Création du processus de génération de canard afin d'avoir des données viables.

*Commentaire(s)*

- J: Est-ce que ça vaut vraiment la peine alors qu'il reste 3 jours effectifs ?
- PY: discussion avec Azzalini, objectif pas de finir parfait mais de montrer que c'est réalisable avec un peu de temps en plus / sur la bonne voie
- C: peut-être plus judicieux de faire un rapport montrant que c'est une direction viable

_Décision_: faire un "bébé-exemple" plutôt que de se lancer dans une implémentation complète

- M: Docker non disponible sur Disco:
  mais intégrable sur calypso, trade-off moins bonne performance sur calypso mais respect la reproductibilité.

*Jeremy* 

Rétro:
 - Correction de bugs îlot UV et fill slicing. 
 - Admin: upload les rapports journalier sur github.

Auj:
  - Fournir test(s) pour team robot
  - Faire des tests avec de nouvelles textures.

*Commentaire(s)*
  - Marco: Valorisation des générations d'Alexandre.



#pagebreak()

*Louis*

_show_
 - Graphique 3D pour le placement du canard. 
 - 4 Graphiques: un pour chaque orientation de canard.

 
Rétro:
 - Test pour la position du support.
  - Pas sûr de la pertinence / du signal amené par les résultats

Auj: 
  - En attente de la fin de la réunion pour allouer

*Alexandre*

Rétro:
  - Le rapport prompt-engineering sera terminé sur temps libre.
  - Test de contrôle pour l'intégration de la partie robot.
Auj:
  - Faire l'interface du site web et vidéo marketing.

*Cédric*

_show_

- Montre la vidéo du dessin du triangle sur le côté du canard

Rétro:
- Test en labo de la partie 

Auj:
  - Debugger et transition de feutres

*Pierre-Yves*

_show_

- Graphique des joints avec les chemins parcours

Rétro:
 - Fixer la pipeline ( pathfinding, safety et computation) et test en condition réel et correction en temps réel

Auj:
 - Dessiner cette après-midi avec des changements de couleurs
 - Hotfix  des traces


Commentaires:

- M: Pourquoi dessiner un triangle est plus difficile que le cercle ?Les mouvements du bras robot sont beaucoup plus amples. 

- P-Y: La solution colle est valide.
- Pour le rendez-vous avec Misk, il faut préparer des modèles atteignables et les vendre, car tout ne sera pas possible donc on doit se concentrer sur les choses réalisables.


#pagebreak()
*Nathan*

Rétro:
  - image docker (difficultés rencontrées sur certain appareil)
  - Containerisation de la partie robot pour éviter les problèmes de versions

Auj: 
 - Passe du temps sur le container
 - Test intégration robot

*Commentaires*

 N : Passer tout le projet en Python 3.11
 
 L : Pas problématique normalement

*Vue d'ensemble*

Demain réunion CTO à 8h.

*Décision*

Comment réussir le point critique de la milestone ?
Il faut se concentrer sur l'orchestration.
