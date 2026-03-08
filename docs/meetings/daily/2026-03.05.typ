#import "./template.typ": *

#show: meeting.with(
  date: datetime(year: 2026, month: 3, day: 5),
  location: [23N415],
  time: [9h00],
  scribe: "K"
)

*Marco* : 

Rétrospective : 

 - Dois push le pull request du benchmark 
 - Dois envoyer un mail un mudry 

Suite :

- Faire des générations sur Disco


*Kevin* : 

- Essayé d'utiliser Disco, bloqué par M. Pignat, ajd c'est bon
- Complété la documentation de recherche solutions AI
- Résolu partiellement les commentaires de PR

Ajd:
- Faire des générations sur Disco
- Finir la PR

*Jeremy* : 

Rétrospective : 

- Finir l'implémentation de l'amélioration du système de détection , presque terminé (corrections pull request)

Suite : 

- Continuer sur d'autres optimisations : Être capable de gérer des formes à dessiner qui sont sur plusieurs faces

*Louis* : 

- Continuer a essayé d'installer le docker de la Solution MV-Adapter (a rencontré pas mal de problèmes de dépendances)

*Nathan* : 

- Continuer sur la fonction get_reacheable (retourne une liste de points TCP & les angles depuis où le bras peut atteindre ce point) + notebook de visualisation 
  va commit 
- Essayer de faire ramasser le stylo dans la simulation, a rencontré quelques problèmes mais fonctionne maintenant

*Pierre-Yves*

- A priori, pas possible de faire des tests sur le robot aujourd'hui
- Discussion avec Loïc, conseillé d'utiliser des solutions déjà existante dans le docker (Move-it to), va implémenter cette solution aujourd'hui

- Suggestion de M.Lettry : Passer sur tests & de la visualisation (graphes) pour chaque petite étape d'amélioration & de nouvelles implémentation (pour les tests de manière générale)

*Cédric* : 

- Problèmes des angles après test sur le bras robot 
- Mettre en place un protocole de test détaillé pour le bras robot afin d'améliorer le debuggage et le error finding (voir avec l'équipe robot)

*Alexandre* : 

- a fait les dernieres modifications nécessaires pour les modèles 3d , à envoyer un mail a darbellay pour les pieces en bois 
- Discussion avec cédric sur l'interet des pieces à se caller sur la plaque en métal (conclusion : semble pas important donc abandonné )
- Partie modélisation terminée , Aujourd'hui : Se met avec la team robot pour travailler

*Commentaires*

- L : présentation de demain à faire
- M : commentaire de Misk(Mudry) (faire des points)
Milestone mort
