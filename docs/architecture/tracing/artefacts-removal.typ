#import "@preview/cheq:0.3.0": checklist
#import "@preview/gentle-clues:1.3.1": *

#set text(font: ("Source Sans Pro", "Source Sans 3"))
#show link: set text(fill: blue)
#show: checklist

#align(center,
  text(size: 2em, weight: "bold")[Plan for update of artefacts removals]
)


= Observed issue

- Artefacts in texture after the palettization (small area of colors stay isolated and
  create to small island to be correctly (due to the pen size) drawn)
- Colored parts of texture that have no reference in the UV map create traces without
  references. For example, when a trace start from a point in the UV map but end
  outside, it isn't processed.


= Planned changes

- Add some blur in the texture before palettization :
  - Should invisibilise the very small isolated artefacts
- Use another palettization method. The current
  #link("https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.quantize")[`quantize()` function]
  with the default
  #link("https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Quantize.MEDIANCUT")[`MEDIANCUT`]
  has the main issue that the dominant color will crush due to the associated weight
  when palettizing.
- Add a mask of UV map to reduce texture image colored only to relative existing UV map
  references.


= Changes done

- [x] Add the `blur()` method in the `Tracer Class`
- [x] Changes the quantize methode, using
  #link("https://stackoverflow.com/questions/73666119/open-cv-python-quantize-to-a-given-color-palette")[`quantize_to_palette()`]
  a function re-used as such from the found source.
- [x] Add a mask function (
  #link("https://learnopencv.com/warp-one-triangle-to-another-using-opencv-c-python/#:~:text=Mask%20pixels%20outside%20the%20triangle,%5D+r2%5B2%5D%5D%20+%20img2Cropped")[used source 1]
  and
  #link("https://pyimagesearch.com/2021/01/19/image-masking-with-opencv/")[used source 2]
  )


= New issues

- After thoses three updates, palettization is now confusing backround of texture (not
  part of UV map) and the texture to applied, so the mask is to be applied after the
  palettization.
- Small artefacts are still remaining. Deactivating the blur proved to be a first good
  step.
- When visualazing the projected traces on the model, a new issue appeared :
  - Possibly due to the new mask, some points are now a bit outside the uv-map making
    their relative trace undrawable.
    - An idea to solve this issue could be to shrink the uv mask to ensure that all
      traces claculated will start/end on the model.
  - Also, some borders between parts of the uv map are very close (up to 1px), thus in
    the palettization/island detection they will get caught in one block.

#error[
  This idea proves to be very difficult to implement. So trying so image processing
  like erode and dilatation seems to be more pertinent.
]

#idea[In the palettized texture, for each artefacts(too small island), change it's color to the dominant one around.]

#align(center)[
  #grid(
    columns: (1fr, 1fr),
    rows: 8cm,
    figure(
      image("./assets/1pixel_marge.png"),
      caption: [Exemple de marge à 1 px entre deux blocs de la UV map],
    ),
    figure(
      image("./assets/1pixel_marge_source.png"),
      caption: [Emplacement de cet exemple],
    ),
  )
]

#align(right)[Jeremy Duc]