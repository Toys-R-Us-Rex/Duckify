#let team = (
  "PY": [Pierre-Yves],
  "A": [Alexandre],
  "J": [Jeremy],
  "C": [Cédric],
  "M": [Marco],
  "N": [Nathan],
  "K": [Kevin],
  "L": [Louis],
  "CTO": underline[Louis Lettru],
  "PO": underline[Cédric Travelletto],
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

#let _milestone-parts = state("milestone-parts")

#let milestone-part(body) = {
  _milestone-parts.update(parts => parts + (body,))
  body
}

#let milestone-parts() = context {
  let parts = _milestone-parts.get()

  block(
    stroke: black,
    inset: 1em,
  )[
    *Milestone parts*
    #list(
      ..parts.map(list.item)
    )
  ]
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
      Weekly Meeting (#date.display("[day].[month].[year]"))
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