#let team = (
  "PY": [Pierre-Yves],
  "A": [Alexandre],
  "J": [Jeremy],
  "C": [Cédric],
  "M": [Marco],
  "N": [Nathan],
  "K": [Kevin],
  "L": [Louis],
)

#let direction-team = (
  "CTO": [Louis Lettru],
  "PO": [Cédric Travelletti],
)

#let meeting(
  date: datetime.today(),
  body
) = {
  set text(
    font: "Source Sans 3",
    lang: "fr"
  )

  show list.item: it => {
    show regex(`[a-zA-Z-]*?\s*:`.text): strong
    it
  }
  
  text(size: 1.6em, weight: "bold")[
    Weekly Meeting (#date.display("[day].[month].[year]"))
  ]
  
  body
}

#let worker-attendees(
  present: auto,
  absent: ()
) = {
  if type(absent) == str {
    absent = (absent,)
  }
  if present == auto {
    present = team.keys().filter(p => p not in absent)
  } else if type(present) == str {
    present = (present,)
  }

  let people = present.map(p => team.at(p)).join(", ")

  [*Workers attendees*: #people]
}


#let direction-attendees(
  people: ()
) = {
  let people = people.map(p => direction-team.at(p)).join(", ")

  [*Direction attendees*: #people]
}