#import "./template.typ": *

#show: meeting.with(
  date: datetime(year: 2026, month: 3, day: 25),
  location: [23N316 / Online],
  time: [9h05],
  scribe: "J",
)
*Kevin*

Retro :
  - a réglé des bogues sur la pipeline GenAI
  - a révisé des PRs
  - a essayé de mettre en place le _repo_ de Nathan (impossible)
Auj : 
  - en attente d'un retour de mail de Lettru
  - continuer la mise en place de FreeU

*Marco*

Retro :
  - mise en pause du côté fine-tuning (cause : contrainte de temps et retours potentiel sur investissement insuffisants) (également en attente du retour de Lettru sur ce sujet. Pas de réponse = abandon) 
  - raffinement de performance du pipeline de GenAi (réduction de \~45s à \~25s par génération en ne chargeant le modèle qu'une seule fois)
Auj : 
  - correction de la PR (du raffinement) puis l'intégrer
  - continuer de travailler sur le benchmark automatisé

*Jeremy*

Retro :
  - a répondu à des demandes de l'équipe robot:
    - a terminé la réduction du nombre de points par trace: p.ex. de 600pts $->$ ~150pts
    - a produit d'autres tests de traces spécifiques
Auj : 
  - résoudre d'autres bugs de fill slicing
  - secondaire: bug à la jointure des îles UV

_*Commentaires:*_
- M: Nouvelle UV map, changements positifs observés ?
  - J: pas de changements significatifs constatés, mais intuitivement, l'ajout d'espacement supplémentaire entre les blocs UV ne peut qu'éviter des problèmes de jointures trop proches

- P-Y : Possible de produire un test avec des points sur tout le canard et un test avec plusieurs couleurs ?
  - J: Bien noté, sera fait aujourd'hui

*Louis*

Retro :
  - a intégré la partie GenAi dans l'interface (avec conversion .obj en .glb et assurance du bon sens du modèle au travers du pipeline)
  - a commencé à travailler sur la résolution du problème du placement optimal du canard et support dans l'espace atteignable du robot. (parallélisation des calculs de tests sur Calypso)
Auj : 
  - continuer à travailler sur la résolution du problème du placement optimal du canard et support 
  - intégration du code robot dans l'interface
  - réviser la future PR de Marco lorsque faite

_*Commentaires:*_
- P-Y : Pense qu'une extension du modèle de test avec le _Planner_ permettrait de trouver les meilleurs cas possibles

*Alexandre*

Retro :
  - a continué à faire des générations pour Marco
  - a commencé le site de démonstration
  - a commencé de produire un rapport sur les générations faites
Auj : 
  - envoyer les travaux de génération fait à Marco
  - finir le rapport de génération
  - si temps à remplir : site de promotion

*Cédric*

Retro :
  - a travaillé sur l'ajout d'arguments au main du pipeline Robot (mode manuel/auto, passer des parties du pipelines,...)
  - a mis à jour et amélioré le système des logs
  
Auj : 
  - travailler avec P-Y pour que le pipeline robot soit prêt à faire des tests cette après-midi

_*Commentaire:*_
 - J: Est-ce que mes observations fournies dans le rapport la semaine passée ont été utiles/intégrées ?
 - C: Elles ont été utiles et intégrées
 
*Pierre-Yves*

Retro :
  - a résolu les problèmes restants (erreurs de code, mise à jour avec la dernière version de PyBullet et compatibilité avec le pipeline de Cédric, agencement des _hover-points_) et a préparé l'intégration du pipeline robot dans _Duckify_
Auj : 
  - effectuer les tests avec le robot 
  - terminer l'intégration de la partie robot dans _Duckify_ (à voir avec Cédric)

_*Commentaires (Problème #1):*_
- N: Problème de fonctionnement de _PyBullet_ avec Python 3.13.X. Apparemment il fonctionnerait avec la 3.11.X, à build en local, mais besoin d'un compilateur

*Nathan*

Retro :
  - a fait tourner le pipeline robot sur d'autres machines (-> problème #1)
Auj : 
  - Compléter le README.md pour décrire le pipeline robot, comment l'utiliser, les dépendances, la mise en place...
  - mettre en place un docker pour résoudre le problème #1

_*Commentaires:*_
- P-Y: Comment va se passer la fin de l'intégration, la résolution du problème #1 ? Dans quel PR ?
- L : Résoudre le problème #1 avec la PR à venir du repo _ur3e_, puis effectuer une autre PR pour l'intégration dans Duckify

  
*Vue d'ensemble* _(Par le chef d'équipe de cette semaine : Marco)_

- Qui sera en télétravail cette après-midi ?
  - Personne, ceux qui sont en télétravail ce matin (N,A,L,K) prévoient de venir
  
- Avancement de l'objectif de la semaine ?
  - sur le pipeline complet : objectif est en cours, intégrations à finir
  - sur la partie GenAi : effectué
  - sur la partie Robot : intégration en cours/à venir
  - sur le changement de couleurs automatiques : _(Alexandre)_ est fonctionnel mais aucun retour actuellement en utilisation intégrée
  
- Décision : Quid de l'intégration du docker GenAI ?
  - L : Ne dois pas être très compliqué à intégrer
  - A,L,M : C'est a fournir en tant que produit au client
  - M : L'intégration du docker passe en priorité de leur tâches prévues : *le choix est arrêté*

- Décision : Idée de la mise en place d'un docker pour la partie robot ?
  - P-Y : Possible d'avoir des versions différente de python ?
    - L : Tout passer en 3.11.X si nécessaire
    - C : Tout mettre dans un docker
  - L : N'est pas la priorité

- Question : (L) Quid du droit de diffusion des images captées du robot en action sur notre Git, site web ?
  - Nathan (après une 1ère réponse a un précédent mail de Mr.Azzalini peu claire) se charge de clarifier la question
