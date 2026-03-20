#import "./template.typ": *

#show: meeting.with(
  date: datetime(year: 2026, month: 3, day: 18),
  location: [23N415 / Online],
  time: [9h05],
  scribe: "K",
  absent: "M"
)

/*
*Marco* : 

Rétrospective : 


Aujourd'hui
*/


*Kevin* : 

- Rétrospective :
  - Commencé / mis à jour la branche d'intégration avec Calypso, adapté pour Disco
  - Encore quelques changements nécessaire

- Aujourd'hui : 
  - Finir la pull request d'intégration du pipeline GenAI

*Louis* : 

- Rétrospective : 
  - Regardé avec Cedric et Pierre-Yves sur les besoins de la partie robot pour l'interface , développé un prototype graphique 
  - Commenté / Répondu a la pull request de Jeremy
- Aujourd'hui : 
  - Regarder avec Kevin pour finaliser la pull request d'intégration GenAI
  - Partie Tracing finie globalement 

*Jeremy* : 

- Rétrospective : 
  - Terminé les corrections d'un bug de remplissage d'ilôt
  - Créer 10 tests différents de dessins / formes à faire sur le canard pour benchmarker à quel point le système de dessin est robuste 
- Aujourd'hui : 
  - Rien à faire 


*Cédric* : 

- Rétrospective :
  - A fait un fichier python d'intégration de la partie robot à la pipeline globale
  - A développer le test de transformation et essayé sur le robot => erreur


- Aujourd'hui : 
  - Corriger le test de transformation (à essayé hier et problèmes de points)

*Pierre-Yves* : 

- Rétrospective : 
  - Plotting des joints : Essaie de fix le problème des joints du robot qui change radicalement entre 2 positions cote à cote => pas idéal / réaliste 


*Nathan* : 

- Rétrospective : 
  - A développé la fonction de filtrage (séparer en deux coté tout les points du modèle 3d)

- Aujourd'hui : 
  - Intégration du bras robot dans la pipeline globale ? 
  - Intégration 

*Alexandre* :

- Rétrospective :
  - Préparé pour la session test robot de hier (s'adapter et s'intégrer dans une pipeline)
  - Préparé les ressorts et les nouveaux sets de supports , Problème : à coupé aléatoirement les supports + pleins de problèmes étrange (comportement bizarre (pince de s'ouvrait pas ou fermait pas))
  
- Aujourd'hui :
  - Va chercher a Hornbach les nouveaux ressorts
  - Session de test robot à 15h
  - Adapter tout le code pour être compatible avec le code de Cédric (code d'intégration de la partie robot à la pipeline globale)

*Redistribution des taches * :
  
- Louis $->$ aider pour résoudre le problème de position instable du bras (w/ PY) / Intégration de la partie robot dans la pipeline globale

- Nathan $->$ Refactor/Fix le code d'Alex sur le mécanisme de transitions de feutres

- Jeremy $->$ Review complète du code d'intégration robot dans la pipeline globale



Bloquants : 

- Le support du robot ne tient pas assez avec le scotch 
  - Solutions potentielles : 
    - Utiliser la colle ?
    - Trou des goupilles plus petit ? -> Doit réimprimer le support -> Doit redemander a Darbellay une plaque en bois avec des trous plus petits
    - Mettre des vis sur du plastique ? -> Pas sur de résister à la pression / abîmer le support
    
    