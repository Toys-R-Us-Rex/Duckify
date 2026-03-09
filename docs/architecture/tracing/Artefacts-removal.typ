#set text(font: ("Source Sans Pro", "Source Sans 3"))
#show link:set text(fill:blue)

#align(
  center,
  text(size: 2em, weight: "bold")[Plan for update of artefacts removals]
)

= Observed issue
- Artefacts in texture after the palettization (small area of colors stay isolated and create to small island to be correctly (due to the pen size) drawn)
- Colored parts of texture that have no reference in the UV map create traces without references. For example, when a trace start from a point in the UV map but end outside, it isn't processed.


= Planned changes
- Add some blur in the texture before palettization :
  - Should invisibilise the very small isolated artefacts
- Use another palettization method. The current #link("https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.quantize")[`quantize()` function] with the default #link("https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Quantize.MEDIANCUT")[`MEDIANCUT`] has the main issue that the dominant color will crush due to the associated weight when palettizing.
- Add a mask of UV map to reduce texture image colored only to relative existing UV map references.

= Changes done :
- Add the `blur()` method in the `Tracer Class`
- Changes the quantize methode, using #link("https://stackoverflow.com/questions/73666119/open-cv-python-quantize-to-a-given-color-palette")[`quantize_to_palette()`] a function re-used as such from the found source.

