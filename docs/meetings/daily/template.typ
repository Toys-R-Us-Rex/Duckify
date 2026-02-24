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

  block[*Attendees*: #people.join(", ")]
}

#let settings(
  location: none,
  time: none,
  scribe: none
) = {
  let elmts = ()

  if location != none {
    elmts.push[*Location*: #location]
  }

  if time != none {
    elmts.push[*Time*: #time]
  }

  if scribe != none {
    elmts.push[*Location*: #team.at(scribe)]
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
      Daily Meeting (#date.display("[day].[month].[year]"))
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