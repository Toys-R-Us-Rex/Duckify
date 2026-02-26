#let team = (
  "PY": [Pierre-Yves Savioz],
  "A": [Alexandre Venturi],
  "J": [Jeremy Duc],
  "C": [Cédric Mariéthoz],
  "M": [Marco Caporizzi],
  "N": [Nathan Antonietti],
  "K": [Kevin Voisin],
  "L": [Louis Heredero],
)

#let attendees(
  present: auto,
  absent: (),
  extra: ()
) = {
  if type(absent) == str {
    absent = (absent,)
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
    elmts.push[*Scribe*: #team.at(scribe)]
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
    font: "Source Sans 3",
    lang: "fr"
  )

  show list.item: it => {
    show regex(`[a-zA-Z-/\s]*?\s*:`.text): strong
    it
  }
  
  block(
    text(size: 1.6em, weight: "bold")[
      Procès verbale de la réunion du #date.display("[day].[month].[year] (Duckifiy)")
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