#set text(font: "Source Sans Pro")

#align(center)[
  #block(inset: 2em)[
    #text(size: 20pt, weight: "bold")[Configuration guide of the 3D printer] \
    #v(0.5em)
    #text(size: 12pt, style: "italic")[Based on the meeting taken with Pr. Darbellay the 17th February 2026]
  ]
]

This document is a retranscription of a discussion between Pr. Darbellay and Alexandre Venturi, it may be not well structured but will contain every information needed to correctly use the program *Prusa Slicer*, the application that take an 3d-model file such as .obj, .step, .stt for exemple and return the path of the printer through the piece.

= Settings Wizard

Configuration source : only Prusa *FFF*

Prusa search : MK3 Family - Original Prusa i3 MK3S & MK3S+ (*0.4mm*)

Filaments -> Profil -> Generic *PLA* (eventually PETG)

Update : keep it checked (if not check it)

Reload from disk : check it

File assotiation : *.3mf* files

View mode : For the beginning keep the *simple* view (If more customisation is requiered change it to *advanced* or *expert*)

_After this step, the wizard will closed and you will be able to see the plate corresponding to the printer._

On the right side of the view, you will see mainly 3 parameters :

- Printing settings : Don't go under 0.10mm
- Filament : Must be Generic PLA
- Printer : Should be Original Prusa i3 MK3S & MK3S+

Check Brim to add it

= Print Settings

This part is related to the setting "Print setting" next to the "Plater" 

Infill : 15% and gyroïd patern (this patern has the characteristic to resist much better pressure from any direction)

Skirt & Brim : Ensure there is a modification in the _Brim_ section
