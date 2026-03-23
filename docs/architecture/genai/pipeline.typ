#import "@preview/cetz:0.4.2": canvas, draw

#set page(
  width: auto,
  height: auto,
  margin: .5cm,
  fill: luma(0%).transparentize(100%)
)

#set text(font: "Source Sans 20", size: 12pt)

#let actor(tl, size, id, name) = {
  draw.rect(
    tl, (rel: size),
    name: id,
  )
  draw.content(
    id,
    align(center, name)
  )
}

#canvas({
  draw.set-style(
    mark: (fill: black),
    line: (mark: (end: ">"))
  )

  actor((0, 0), (2, -2), "client")[
    Client\
    _(client.py)_
  ]
  
  actor(
    (rel: (10, 0), to: "client.north-east"),
    (3, -2),
    "server"
  )[
    Server (Flask)\
    _(server.py)_
  ]
  
  actor(
    (rel: (0.5, -3), to: "server.south-west"),
    (2, -1),
    "mv-adapter"
  )[
    MV-Adapter
  ]

  draw.line(
    (rel: (0, .5), to: "client.east"),
    (rel: (0, .5), to: "server.west"),
    name: "step1"
  )
  draw.content("step1.mid", anchor: "south", padding: 3pt, align(center)[Prompt + model\ + parameters])

  draw.line(
    (rel: (.5, 0), to: "server.south"),
    (rel: (.5, 0), to: "mv-adapter.north"),
    name: "step2"
  )
  draw.content("step2.mid", anchor: "west", padding: 3pt)[Slurm job]

  draw.line(
    (rel: (-.5, 0), to: "mv-adapter.north"),
    (rel: (-.5, 0), to: "server.south"),
    name: "step3"
  )
  draw.content("step3.mid", anchor: "east", padding: 3pt, align(center)[Textured model\ (.glb)])

  draw.line(
    (rel: (0, -.5), to: "server.west"),
    (rel: (0, -.5), to: "client.east"),
    name: "step4"
  )
  draw.content("step4.mid", anchor: "north", padding: 3pt, align(center)[Texture + metadata\ (.zip)])

  draw.content(
    (rel: (-0.5, 2), to: "step1.mid"),
    text(fill: green.desaturate(20%).darken(20%))[*SSH Tunnel*],
    padding: 3pt,
    name: "ssh"
  )

  draw.line(
    "ssh.west", (rel: (-1, 0)),
    stroke: gray,
    mark: (end: "|", scale: 3)
  )

  draw.line(
    "ssh.east", (rel: (1, 0)),
    stroke: gray,
    mark: (end: "|", scale: 3)
  )
  draw.rect(
    (rel:(-2, 1), to: "server.north-west"), 
    (rel:(2, -1), to: "mv-adapter.south-east"), 
    stroke: orange,name: "disco"
  )
  draw.content(("disco.north"), anchor: "south", padding: 3pt, align(center)[*Disco.hevs.ch*])

  draw.rect(
    (rel:(-1, 1), to: "client.north-west"), 
    (rel:(1, -1), to: "client.south-east"), 
    stroke: orange,name: "local-pc"
  )
  draw.content(("local-pc.north"), anchor: "south", padding: 3pt, align(center)[*Local PC*])
})