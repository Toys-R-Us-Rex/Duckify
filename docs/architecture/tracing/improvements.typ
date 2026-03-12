#import "@preview/cheq:0.3.0": checklist
#let date = datetime(year: 2026, month: 3, day: 11)

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

=== Color quantization

To improve color quantization, multiple solutions are possible:
- find a better method than median cut
- "ignore" background color (i.e. regions outside the UV map)
- improve color contrast (e.g. remove reflections)

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
  - Out of bounds
  - UV seams
]

#block(
  width: 100%,
  stroke: 1pt,
  inset: 1em,
  breakable: false
)[
  *Jeremy*
  - [x] Finalize color quantization
  - Identify and solve fill slicing issues
]

#block(
  width: 100%,
  stroke: 1pt,
  inset: 1em,
  breakable: false
)[
  *TBD*
  - Unreachable areas
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