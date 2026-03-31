#import "@preview/cheq:0.3.0": checklist
#let date = datetime(year: 2026, month: 3, day: 25)
#show link: it => text(fill: blue, it)

#set document(
  author: ("Jeremy Duc",),
  date: date,
  title: "Fill slicing debug 2"
)

#set text(
  font: ("Source Sans 3", "Source Sans Pro")
)
#show: checklist

= Fill slicing debug 2 (#date.display("[day].[month].[year]"))

== Foreword

After the implementation of the reduction of points per trace (PR #92 #footnote[#link("https://github.com/Toys-R-Us-Rex/Duckify/pull/92")[PR #92 — reduce number of points in contours]]), a new error appeared during testing. It's been resolved in the PR #96 #footnote[#link("https://github.com/Toys-R-Us-Rex/Duckify/pull/96")[PR #96 — fill slicing debug 2]].

== Error

==== Explanation

When processing the clown texture, the following error appeared:

```
shapely.errors.GEOSException: TopologyException:
side location conflict at 0.62652522935779809 0.19902522935779812
```

This exception happen because Shapely is working on an *invalid* polygon. THe source of these invalid polygons is the contour simplification. It sometimes produces self-intersecting or unvalid geometries#footnote[#link("https://shapely.readthedocs.io/en/latest/reference/shapely.make_valid.html")[shapely.make_valid documentation]].


==== Solution

Use a validity check on the polygon before using it. If the polygon is invalid, use the `shapely.make_valid()` method to cope with it.

---

== Conclusion

The chages made with the reduction created an unforseen issue. Up to my actual tests and knowledge, the current implementation is working. However I can't garanty a total efficiency and therfore suggest to make, if time allow, a systematic test over diverse generated textures to ensure reliability.


#align(right)[Jeremy Duc]