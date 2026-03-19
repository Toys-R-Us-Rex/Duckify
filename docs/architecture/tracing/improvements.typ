#import "@preview/cheq:0.3.0": checklist
#let date = datetime(year: 2026, month: 3, day: 11)
#show link: it => text(fill: blue, it)

#set document(
  author: ("Louis Heredero", "Jeremy Duc"),
  date: date,
  title: "Tracing Algorithm Improvements"
)

#set text(
  font: ("Source Sans 3", "Source Sans Pro")
)
#show: checklist

= Tracing Algorithm Improvements (#date.display("[day].[month].[year]"))

== Known issues

- When dealing with AI generated textures, some color artifacts may appear, producing very small islands that should otherwise be of the surrounding color
- Due to the way the texture is generated, islands may extends out of the UV mapped area, rendering simple 3D projection impossible
- The default color quantization method (MEDIANCUT) is heavily biased by the primary color, which "floods" the other colors
- When a particular pattern covers multiple UV islands (i.e. crosses a UV seam), multiple traces will be produced, splitting the shape at the seam
- The path produced by the tracer do not take into account the reachability of the zones, and will produce undrawable traces (e.g. edges of the eyes)
- Fill slicing sometimes fail, inverting inside and outside areas of color islands

== Possible improvements

=== Artifacts

To reduce small color artifacts, a potential solution is to blur the input texture / dilate the palettized texture so that tiny holes are filled

=== Out of bounds

Possible solutions to the islands extending out of the UV map are:
- compute the intersection between UV geometries and island borders
- extrapolate projection outside of UV triangles
- apply a shrinked mask to only get polygons inside the UV map or shrink the polygons after contour detection

#figure(
  image("assets/uv_boundary_cases_cropped.svg"),
  caption: [UV boundary crossing cases]
)

=== Color quantization (palettization)

==== Issue
 The default color quantization method (MEDIANCUT) is heavily biased by the primary color, which "floods" the other colors. This bias is inherent of the method — as a bucket-based algorithm, it splits color space at the statistical median of pixel count, allocating palette entries proportionally to color frequency. In our pipeline this translate in the black color, beeing the one replacing elements not in the UV mask applied on the texture, thus having heavy weight.

==== Solution
Using a KNN-based approach #footnote[#link("https://stackoverflow.com/questions/73666119/open-cv-python-quantize-to-a-given-color-palette")[StackOverflow KNN solution]] solves this issue: instead of building the palette from pixel frequency, the model is trained on a fixed, predefined palette and assigns each pixel to its nearest color in that space — regardless of how dominant that color is in the image. This eliminates the frequency bias introduced by MEDIANCUT. This approach also allows specific colors (e.g. the background black) to be explicitly excluded from the palettization process.

=== UV seams

To avoid splitting contours at UV seams, there could be a post-processing step which links polygons with overlapping (i.e. very close) points

=== Unreachable areas

A mask could be defined to limit drawing to manually selected "drawable" areas

=== Fill slicing

Filtering out very small islands should reduce mathematical errors

== Attack plan

#block(
  width: 100%,
  stroke: 1pt,
  inset: 1em,
  breakable: false
)[
  *Louis*
  - [/] Out of bounds
  - [?] UV seams
  - [?] Unreachable areas
]

#block(
  width: 100%,
  stroke: 1pt,
  inset: 1em,
  breakable: false
)[
  *Jeremy*
  - [x] Finalize color quantization
  - [x] Small artefacts replacement
  - [x] Identify and solve fill slicing issues
]

== Is the current solution the right one ?

#table(
  columns: (1fr, 1fr),
  table.header[*Yes*][*No*]
)[
  It works for simple textures
][
  It breaks for more complex textures (currently)
][
  Current issues seem to be solvable without complete refactoring
][
  Some issues (e.g. UV seams) seem complicated to solve completely / elegantly
]

In conclusion, we believe this is still a viable solution

#v(1fr, weak: true)

#align(right)[Jeremy Duc, Louis Heredero]