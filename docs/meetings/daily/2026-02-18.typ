#import "@preview/suiji:0.5.1": *
#import "./template.typ": meeting, attendees, team

#show: meeting.with(
  date: datetime(year: 2026, month: 2, day: 18)
)

#attendees(
  absent: ("K", "N")
)

#let rng = gen-rng(15)
#let (rng, order) = shuffle(rng, team.values())

- P-Y : Tourner le scribe\
    $->$ Ordre: #order.join(", ")
- A: Impressions devraient être finies d'ici fin de W2
- P-Y: Expert en connaissance, pas que tout soit fini
- L: Remplir les milestones pour 10h30
- P-Y: Accès à la simulation
- P-Y: besoin d'explorer un peu les librairies / la simulation pour définir les milestones
- L: Chacun faire une liste de questions pour le client pour la fin de la journée (15h, 15h30)
- P-Y: Où mettre liens/repo pour partage
- L: Si lien, on peut mettre dans un dossier doc, pour les fichiers plus gros, éventuellement OneDrive
- L: Mettre les tâches sur Jira