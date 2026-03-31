#import "@preview/cheq:0.3.0": checklist
#let date = datetime(year: 2026, month: 3, day: 3)
#show link: it => text(fill: blue, it)

#set document(
  author: ("Jeremy Duc",),
  date: date,
  title: "Border detection refinement"
)

#set text(
  font: ("Source Sans 3", "Source Sans Pro")
)
#show: checklist

= Border detection refinement (#date.display("[day].[month].[year]"))

== Context

Up to now, the island detection only retrieve the outer contour of each color island. The update work to also retrieve the internal one is recorded in PR #42 #footnote[#link("https://github.com/Toys-R-Us-Rex/Duckify/pull/42")[PR #42 — border detection refinement]] and described in this document.

== Nested contours detection update

=== Explanation

The current shortcomings are due to `cv2.RETR_EXTERNAL`, that do not retrieve inner contour datas. This result in islands with holes had them not cutted out.

=== Solution

Use `cv2.RETR_CCOMP` instead of `cv2.RETR_EXTERNAL`#footnote[#link("https://learnopencv.com/contour-detection-using-opencv-python-c/")[source of information about the methods]]. This method retrieves all the contours in an image. Along with that, it also applies a 2-level hierarchy to all the shapes or objects in the image.

To work with that, a new `Hierarchy` dataclass has been implemented to handle the parent/child relationships. 

This updated processing induced two cases of island construction :
 + Contours with no parent and no child are making `Island` with only one outer border
 + Contours with children are making `Island` with an `inner_borders` list that record all hole contours and the outer border

#grid(
  columns: (1fr, 1fr),
  gutter: 1pt,
  figure(
    image("assets/before-nested.png", height: 150pt),
    caption: [Before — no nested contours]
  ),
  figure(
    image("assets/after-nested.png", height: 150pt),
    caption: [After — included nested contours]
  )
)

=== Conclusion

The detection is now now correctly handling the nested contours. Hole areas are excluded from the fill slicing and tracing, thus not processed furter the pipeline.


#align(right)[Jeremy Duc]
