#import "./template.typ": *

#show: meeting.with(
  date: datetime(year: 2026, month: 3, day: 31),
  location: [23N314],
  time: [9h05],
  scribe: "K"
)

*Marco* :

Rétrospective : 
  - Continué le fine-tuning après la data augmentation:
    - Pas de résultats probants , le modèle apprend mais pas ce qu'on souhaite , conclusion : pas possible d'implémenter en prototype
    - Intégration du benchmark dans la pipeline genai (collaboration avec Kevin)
Aujourd'hui :
  - Portfolio

*Kevin*

- Rétro :
  - Review PR intégration GenAI dans l'interface
  - Avec Marco en peer programmming : intégration du benchmark de Marco
- Auj :
  - Intégration docker de M. Heredero (MV-Adapter)
  - Portfolio

*Alexandre*:

- Rétrospective:
  - Continué le site web de promotion, ajouté un div "Try it now" avec des images par défaut


- Aujourd'hui :
  - Continuer le site
  - Montage vidéo
  - Portfolio


*Jeremy* :

- Rétrospective : 
  - Effectué le changement : pouvoir exclure des couleurs lors du pipeline pour qu'elles ne soient pas dans les traces
  - Fourni les traces (discuté avec PY et Marco)
  - Commencé / fini de mettre à jour la documentation de la team tracing (ses contributions)
  - Passage au labo pour observé la mise en oeuvre de changements effectués

- Aujourd'hui :
  - _Dilemme_ : Aider les autres ou faire en sorte que l'espacement des traits dépend de l'épaisseur du stylo

_Question de Marco_ sur la documentation de leur collaboration (entre Jeremy et Marco) ? -> Jeremy va formaliser et détailler cette documentation pour le portfolio


*Louis* :

- Rétrospective : 
  - Intégré la partie Robot dans l'interface :
    - On peut faire la calibration , transformation et traces TCP , partie pathfinding à intégrer
    - Connexion robot fonctionnelle

- Aujourd'hui :
  - finir cette intégration de la partie robot :
    - Moins de visualisation que prévu

*Nathan* :

- Rétrospective : 
  - Conteneurisation du projet Duckify

- Aujourd'hui :
  - Continuer sur la conteneurisation
  - aider les autres teams / review les PR

*Cédric* :

- Rétrospective : 
  - Tests au labo :
    - Faire en sorte qu'on puisse tourner le canard pour dessiner -> Fonctionnel

- Aujourd'hui :
  - Mode force : ne pas vas s'écraser quand il dessine -> sécurité en plus 
  - Aider _PY_ sur les tests



*Pierre-Yves*:

- Rétrospective : 
  - Plot qui compare toute les solutions path tracing
    - Refinement & Debugging pour comprendre où est le problème identifié avec le plot  

- Aujourd'hui :
  - Continuer à corriger le problème identifié avec le plot
  - Labo & Test
