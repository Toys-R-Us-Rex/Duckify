#import "./template.typ": *

#show: meeting.with(
  date: datetime(year: 2026, month: 3, day: 9),
  location: [23N314],
  time: [9h00],
  scribe: "PY",
  absent: "M"
)

*Kevin* : 

retrospective:
- A créé un Excel qui répertorie ses créations
- A résolu un problème sur la génération de canards 
- (montre un exemple de canard vert avec une étoile jaune: prompt + image correspondante)
L: les points ça va être complique à faire
plan:
K: va se concentrer sur text2texture

J: avoir un set mock et un vrai set
C: (idem)
K: ok


*Team Tracing*

*Louis* :
- pas de nouvel avancement depuis le dernier meeting sur le tracing
- Investissement sur le Docker de MV Adapter, mis en pause pour l'instant

plan: va soit continuer l'intégration Docker ou continuer le tracing. Il est libre

*Jeremy* :
- a commencé a traiter les artefacts / îlots de couleur

*Team LLM*

- Reproduire l'environnement complet GenAI sur Docker est compliqué. Mais ce n'est pas le focus pour le moment

*Alex*

- a adapté le design pour un feutre.

plan: faire le mouvement entre différents feutres. 

*Cédric*

Rétrospective labo de vendredi:
- Problème de précision : a cause de la surface, précision de calibration

plan: a dessiner une ligne sur un canard.
Question sur le jour off mardi -> R: seulement demi-journée ( après midi)

*Nathan*

- A mis en place la simulation avec tous les objets dans Gazebo
- Fonction pour attraper un feutre
- Fichier MD tuto setup des objets dans la simulation.

plan: get_reachable

*P-Y*

- Regarder pour discuter des 3 solutions: choix fait $->$ PyBullet. Restructuration nécessaire mais pas immense. 
- Calibration plus précise notamment pen pressure. Tout ce qui faut pour améliorer la précision au delà du millimètre (Discussion avec Lettry)


*Commentaire*

- L : Faut pas penser faut faire (citation approximative de M. Lettry)
- C : conserver la seed des générations
- C : Mettre les méta-datas, pourraient être utiles

*Post-Daily Meeting*

- Marco: Mise en place d'une solution on premise pour IMAGE2TEXTURE, il n'y a plus d'appel sur l'api chatgpt pour générer l'image de canard
