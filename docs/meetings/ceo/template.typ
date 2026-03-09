#let team = (
  "PY": [Pierre-Yves Savioz],
  "A": [Alexandre Venturi],
  "J": [Jeremy Duc],
  "C": [Cédric Mariéthoz],
  "M": [Marco Caporizzi],
  "N": [Nathan Antonietti],
  "K": [Kevin Voisin],
  "L": [Louis Heredero],
  "CTO": underline[M. Lettru],
  "PO": underline[M. Travelletto],
  "CEO": underline[M. Misk],
)

#let attendees(
  present: auto,
  absent: (),
  extra: ()
) = {
  if type(absent) == str {
    absent = (absent,)
  }
  if type(extra) != array {
    extra = (extra,)
  }
  if present == auto {
    present = team.keys().filter(p => p not in absent)
  } else if type(present) == str {
    present = (present,)
  }

  let people = present.map(p => team.at(p)) + extra

  block[*Présent*: #people.join(", ")]
}

#let settings(
  location: none,
  time: none,
  scribe: none
) = {
  let elmts = ()

  if location != none {
    elmts.push[*Lieu*: #location]
  }

  if time != none {
    elmts.push[*Heure*: #time]
  }

  if scribe != none {
    if type(scribe) != array {
      scribe = (scribe,)
    }
    let title = if scribe.len() == 1 [Scribe] else [Scribes]
    elmts.push[*#title*: #scribe.map(s => team.at(s)).join[, ]]
  }

  if elmts.len() == 0 {
    return none
  }

  block(elmts.join[ | ])
}

#let meeting(
  date: datetime.today(),
  present: auto,
  absent: (),
  extra: (),
  location: none,
  time: none,
  scribe: none,
  body
) = {
  set text(
    font: ("Source Sans 3", "Source Sans Pro"),
    lang: "fr"
  )

  show quote.where(block: true): block.with(
    stroke: (left: gray + 2pt),
    width: 100%,
    inset: .8em
  )
  show quote.where(block: true): set par(justify: true)

  
  block(
    text(size: 1.6em, weight: "bold")[
      Procès verbal de la réunion du #date.display("[day].[month].[year]") (Duckify)
    ]
  )

  block(
    width: 100%,
    stroke: 1pt,
    inset: .8em,
    radius: .4em,
    {
      attendees(
        present: present,
        absent: absent,
        extra: extra
      )

      settings(
        location: location,
        time: time,
        scribe: scribe
      )
    }
  )
  
  body
}

#let blocker = highlight(fill: red)[BLOCKER]