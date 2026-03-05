#import "./template.typ": *

#show: meeting.with(
  date: datetime(year: 2026, month: 2, day: 27),
  location: [23N316],
  time: [15h00],
  scribe: "L"
)

- réduire la taille du stylo ? pas forcément nécessaire pour le milestone

- restructuration du code nécessaire, centralisation

- Jeremy: organisation plus hiérarchique

- Semaine 3:
  #table(
    columns: 2,
    table.header[*Rôle*][*Personne*],
    [Overview], [Nathan],
    [Robot], [Cédric],
    [3D], [Alex],
    [Gen AI], [Kevin],
    [Tracing], [Jeremy]
  )
