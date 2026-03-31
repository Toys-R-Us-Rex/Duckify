#import "./template.typ": *

#show: meeting.with(
  date: datetime(year: 2026, month: 3, day: 26),
  location: [23N316],
  time: [13h00],
  scribe: "J",
  absent: ("A","C","K","N", "L")
)

#import "@preview/cheq:0.3.0": checklist
#let date = datetime(year: 2026, month: 3, day: 26)
#show link: it => text(fill: blue, it)

#set document(
  author: ("Jeremy Duc",),
  date: date,
  title: "Preparation of CEO's presentation"
)

#set text(
  font: ("Source Sans 3", "Source Sans Pro")
)
#show: checklist

== Context

This report a meeting made between representatives of teams GenAI (Marco), Tracing (Jeremy) and Robot (Pierre-Yves) in order to inquire about textures to prepare to be drawn for/during the final CEO's presentation.

== Objectives

Our main goal is to decide suited prompts then textures.

== Prompts

We met on the following prompts :
+ Army duck : `Yellow duck disguised as militarymen, big blue star`
+ Clown duck :`Yellow duck disguised as a clown, red, green, blue, yellow pattern`
+ Firefighter duck : `Yellow duck disguised as a fireman, red coat, blue stripes`
+ ISC flocked duck : `Yellow duck with "ISC" written on the body`
+ Heart's duck : `Yellow duck with a red heart on the head`

== Textures

The following are the generated textures, using the GenAI pipeline with the above prompts.

#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 1pt,
  figure(
    image("assets/army.png", height: 150pt),
    caption: [Army duck]
  ),
  figure(
    image("assets/clown.png", height: 150pt),
    caption: [Clown duck]
  ),
  figure(
    image("assets/firemen.jpg", height: 150pt),
    caption: [Firefighter duck]
  ),
)

#grid(
  columns: (1fr, 1fr),
  gutter: 1pt,
  figure(
    image("assets/isc.png", height: 150pt),
    caption: [ISC flocked duck]
  ),
  figure(
    image("assets/heart.jpg", height: 150pt),
    caption: [Heart's duck]
  ),
)

== Decision
Based on the texture results (only the best ones by prompt are shown up here) we conclude that, ranked in difficulty ascendant order, we should only try the army, clown and firefighter duck. 

We justify this decision because they represent a convenient trade-off between simplicity (Army duck), the changes of pens (Clown duck) and difficulty (Firefighter). Also, motives are crisper and will better represent the project abilities. (different motives, in differents parts of the duck, multiple colors)