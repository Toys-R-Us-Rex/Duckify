#import "@preview/cheq:0.3.0": checklist

#show: checklist

#set text(font: ("Source Sans 3", "Source Sans Pro"))
#set heading(
  numbering: "(A.1)"
)

#let test-names = (
  "triangle",
  "circle",
  "circle_full",
  "triangle_on_bill",
  "triangle_on_back",
  "eyes",
  "torso",
  "on_head",
  "3_colors",
  "full_body_line",
)

#let quality = (
  FAILED: highlight(fill: red)[failed],
  BAD: highlight(fill: orange)[bad],
  OK: highlight(fill: yellow)[ok],
  GOOD: highlight(fill: green)[good],
  TBD: [_tbd_],
)

#let test = block.with(
  width: 100%,
  breakable: false,
  stroke: 1pt,
  inset: 1em
)

#let test-img(i) = {
  let name = test-names.at(i - 1)
  let path = "/assets/textures/test/test_" + str(i) + "_" + name + ".jpg"
  figure(
    image(path, width: 4cm),
    caption: [#name.replace("_", " ")],
    supplement: [Test]
  )
}

#text(size: 2em)[*Robot Testing Protocol*]

- *Date*: 18.03.2026
- *Start time*: 15h00
- *People*:
  - Robot 1:
    - Cédric
    - Pierre-Yves
  - Robot 2:
    - Nathan
    - Alexandre
  - Supervisor
    - L. Azzalini

#line(length: 100%)

= Robot 1

== General Procedure
+ Initialize robot
+ Setup workspace
  + Place support
  + Place cardboard
  + Place duck
+ Connect to the robot
  + Check connection
  + Reset arm (position, gripper)
+ Verify transformation with hardcoded point
+ Run trace tests (see @robot-1-tests)
+ Reset robot
+ Clear workspace
  + Remove duck
  + Remove cardboard
  + Remove support

#pagebreak(weak: true)

== Trace Tests <robot-1-tests>

#columns(2)[
  #test[
    1. Triangle
    #test-img(1)

    - [ ] Simulation ok
    - [ ] Start position ok
    - [ ] Entry ok
    - Trace quality: #quality.TBD
    - [ ] Exit ok
  ]

  #test[
    2. Circle
    #test-img(2)

    - [ ] Simulation ok
    - [ ] Start position ok
    - [ ] Entry ok
    - Trace quality: #quality.TBD
    - [ ] Exit ok
  ]

  #test[
    3. Circle (filled)
    #test-img(3)

    - [ ] Simulation ok
    - [ ] Start position ok
    - [ ] Entry ok
    - Trace quality: #quality.TBD
    - Fill quality: #quality.TBD
    - [ ] Exit ok
  ]

  #test[
    4. Triangle (bill)
    #test-img(4)

    - [ ] Simulation ok
    - [ ] Start position ok
    - [ ] Entry ok
    - Trace quality: #quality.TBD
    - [ ] Exit ok
  ]

  #test[
    5. Triangle (back)
    #test-img(5)

    - [ ] Simulation ok
    - [ ] Start position ok
    - [ ] Entry ok
    - Trace quality: #quality.TBD
    - [ ] Exit ok
  ]

  #test[
    6. Eyes
    #test-img(6)

    - [ ] Simulation ok
    - [ ] Start position ok
    - [ ] Entry ok
    - Trace quality: #quality.TBD
    - [ ] Exit ok
  ]

  #test[
    7. Torso (target pattern)
    #test-img(7)

    - [ ] Simulation ok
    - [ ] Start position ok
    - [ ] Entry ok
    - Trace quality: #quality.TBD
    - [ ] Exit ok
  ]

  #test[
    8. Head (target pattern)
    #test-img(8)

    - [ ] Simulation ok
    - [ ] Start position ok
    - [ ] Entry ok
    - Trace quality: #quality.TBD
    - [ ] Exit ok
  ]

  #test[
    9. 3-colors
    #test-img(9)

    - [ ] Simulation ok
    - [ ] Start position ok
    - [ ] Entry ok
    - Trace quality: #quality.TBD
    - [ ] Exit ok
  ]

  #test[
    10. Body lines
    #test-img(10)

    - [ ] Simulation ok
    - [ ] Start position ok
    - [ ] Entry ok
    - Trace quality: #quality.TBD
    - [ ] Exit ok
  ]
]

/*
- Tester la conversion / transformation (position du support et du canard)
  - Donner 1 point
  - `transformation.py:test_transformation()`
    - Possible d'ajuster la matrice de transformation

- Pathfinding:
  - Mettre le bras dans une position (freedrive) $->$ go to point
*/