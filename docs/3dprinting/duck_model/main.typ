#set text(font: "Source Sans Pro")

#align(center)[
  #block(inset: 2em)[
    #text(size: 20pt, weight: "bold")[Duck model documentation] \
    #v(0.5em)
    #text(size: 12pt, style: "italic")[Design confirmed by CEO]
  ]
]

This doc will give the basic information about the 3D model of duck we will use during the project. The model was decided during a meeting with our CEO, CTO and product owner. You can find the minutes #link("https://github.com/Toys-R-Us-Rex/Duckify/commit/a0165bab2c557b488c5e862b679adeffa8de1985")[
  *here*
].

It doesn't mean we will only stay on this model but at the state of the project (03.03.2026), we will.

Here is the model :

#figure(
  image("duck_model_3.png", width: 70%),
)

Based on the application Prusa slicer, the duck can be contained in a 3D rectangle of 74.23mm, 101.35mm, 103.83mm.

#figure(
  image("size.png"),
)

The printing time is evaluated at 9h without support but expertes strongly suggest us to add support by default to avoid printing issue so it goes up to 10 hours.

#figure(
  image("printing_time.png"),
)

The weight is estimated at 84.81g for a cost of 2CHF based on an #link("https://3dprintingcostcalculator.com/fr")[*estimation website*].