#import "@preview/cheq:0.3.0": checklist
#let date = datetime(year: 2026, month: 3, day: 20)
#show link: it => text(fill: blue, it)

#set document(
  author: ("Jeremy Duc",),
  date: date,
  title: "Duck UV Map rearrangement"
)

#set text(
  font: ("Source Sans 3", "Source Sans Pro")
)
#show: checklist

= Duck UV Map rearrangement (#date.display("[day].[month].[year]"))

== Context

During texture testing in the tracing pipeline, jumping cross-UV-block traces were observed. The too near proximity of blocs on the UV map is certainly the cause of it. A sub-pixel proximity between vertices belonging to different blocks has been observed on Blender. 

The work described here is recorded in the PR #90 #footnote[#link("https://github.com/Toys-R-Us-Rex/Duckify/pull/90")[PR #90 — JIRA-159: UV map correction]].


#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 1pt,
  figure(
    image("assets/1pixel_marge.png", height: 150pt),
    caption: [Sub-pixel proximity]
  ),
  figure(
    image("assets/1pixel_marge_source.png", height: 150pt),
    caption: [Location of figure 1]
  ),
  figure(
    image("assets/example-jump.png", height: 150pt),
    caption: [Jumping trace example]
  ),
)

== UV map rearrangement

==== Explanation

When two UV islands are very close together, their border vertices can fall within the same pixel on the texture image. This causes the tracer to incorrectly link contour points across island boundaries, producing spurious traces that cross from one UV block to another.

==== Solution

Rearrange the blocs of the  UV map in Blender. It should ensure sufficient spacing between all UV islands.

#grid(
  columns: (1fr, 1fr),
  gutter: 1pt,
  figure(
    image("assets/uv-map-before.png", height: 150pt),
    caption: [Before — UV islands too close]
  ),
  figure(
    image("assets/uv-map-after.png", height: 150pt),
    caption: [After — UV islands properly spaced]
  )
)

==== Conclusion

This update (followed by an update of the drawable masl) ensure that there is always space between different blocks of the UV map. The pre-change observed issue didn't reappear.

=== Self-relfection
- If existing, a solution that implies a root change in a pipeline can be easier to do. It will also not affect the already implemented architecture.

#align(right)[Jeremy Duc]