#import "./template.typ": meeting, attendees, team, blocker
#show figure: set align(start)
#show: meeting.with(
  date: datetime(year: 2026, month: 2, day: 26),
  extra: ([Elan Misk (CEO)],),
  location: [23N308],
  time: [8h15],
  scribe: "J"
)

=== Contexte
Cette réunion a été mise en place dans le but que l'équipe travaillant sur le projet Duckify puisse présenter a M.Misk le pipeline de production prévu selon plusieurs alternatives et l'interoger sur certains choix à arrêter.

=== Dicussions
+ *Proposition de l'équipe*
  - Un modèle de canard unique, sur lequelle la texture désirée par le consommateur serait appliquée
  - *Décision de M.Misk* : L'idée d'un modèle de canard fixe est validée

+ *Proposition de l'équipe*
  - Utiliser un modèle de canard précis, selon visualisation 1 dans *Annexes* 
  - *Décision de M.Misk* : Ce modèle ne correspond pas aux attentes. Demande de recevoir une sélection de modèles plus arrondis pour arrêter un choix. Propose à l'équipe d'en chercher sur "BlenderMarketPlace".

+ *Proposition de l'équipe*
  - Utiliser un modèle de canard précis, selon visualisation 1 dans *Annexes* 
  - *Décision de M.Misk* : Ce modèle ne correspond pas aux attentes. Demande de recevoir une sélection de modèles plus arrondis pour arrêter un choix.

+ *Proposition de l'équipe*
  - Arrêter un choix sur le processus de génération de la texture a appliquée au canard 
  - *Commentaire de M.misk* : Les alternatives présentées ne sont pas suffisament claire et sourcées (en coût) pour qu'une décision soit prise.

+ *Information de l'équipe*
  - Les contraintes suivantes sont a prendre note :
    - Lors de la phase d'application de la texture sur le canard, le nombre de couleurs sera limité (~ 4 à 6)
    - Le temps de production d'un canard est estimé > 10h (~10 min. de génération de texture, ~10h d'impression 3d du canard et ~1h d'application de la texture sur le canard)

=== Planification
La prochaine réunion a été planifiée au mardi 3 mars à 10h30.

=== Annexes
#align(left)[
  #figure(
    image("../assets/duck.png", width: 30%),
    caption: [
      Modèle proposé lors de la réunion (rejeté)
    ],
  ) 
]