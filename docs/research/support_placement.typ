#set text(
  font: ("Source Sans 3", "Source Sans Pro")
)

#set heading(numbering: "1.1")
#show heading.where(level: 1): set heading(numbering: "1.")

#set document(
  author: "Louis Heredero",
  date: datetime(year: 2026, month: 3, day: 31),
  title: [Duck support placement optimization]
)

#let join-authors(authors, sep: ", ", last-sep: " & ") = {
  let authors = authors
  let n = authors.len()
  if n >= 2 {
    authors = authors.slice(0, n - 2) + (authors.slice(-2).join(last-sep),)
  }
  return authors.join(sep)
}

#let multiref(..args, default: ",", last: " and") = context {
  let tags = args.pos()
  let fig = query(tags.first()).first()
  let suppl = fig.supplement

  if tags.len() >= 2 { suppl + "s" } else { suppl }
  ref(tags.first(), supplement: "")
  for key in tags.slice(1, -1) {
    ref(key, supplement: default)
  }
  if tags.len() >= 2 {
    ref(tags.last(), supplement: last)
  }
}

#align(center, context text(2em, weight: "bold", document.title))

#context {
  let authors = document.author
  if type(authors) != array {
    authors = (authors,)
  }
  text(size: 1.2em)[*Written by:* #join-authors(authors)]
}

= Goal

Pierre-Yves asked the team whether it was possible for someone to look into the analysis of the support placement. The idea was to test many positions to find out whether (1) the current position was good and (2) what the optimal position would be.

Formally, the objective was to determine where the duck support should be to maximize the number of accessible points on the duck.

= Method <method>

I created a first script to randomly generate a number of points on the duck's surface to have a well spread out sample.

Then I created a script to generate many random support placements in a defined area around the robot (a half-donut), with varying heights. These placements (position + rotation) were then fed to PyBullet to analyze whether valid solutions existed for each point on the duck.

To maximize efficiency, I used multiprocessing on Calypso to split the workload across 32 processes.

= Results <results>

Using the method described in @method, I collected 54'954 datapoints, i.e. support placements.

With the help of Claude, I visualized the results as shown below. In #multiref(<cloud-0>, <cloud-90>, <cloud-180>, <cloud-270>), we can see all the tested placements (`(0,0,0)` origin, i.e. the top of the support). The color indicates the ratio of points with a valid IK solution (i.e. without any collision). Each figure shows a different rotation of the duck, starting with 0°, with the duck facing towards the positive X axis.

#for i in range(4) {
  let angle = i * 90
  [
    #figure(
      image("assets/cloud_a" + str(angle) + ".png", height: 9cm),
      caption: [3D accessibility point cloud (angle=#angle°)]
    ) #label("cloud-" + str(angle))
  ]
}

Due to the high density of points, making the 3D plots hard to analyze, I also created 2D heatmaps from different point of views, as shown in #multiref(<heatmap-top>, <heatmap-front>, <heatmap-side>).

#figure(
  image("assets/heatmap_top.png", width: 80%),
  caption: [2D accessibility heatmap (top view, X/Y axes)]
) <heatmap-top>

#figure(
  image("assets/heatmap_front.png", width: 80%),
  caption: [2D accessibility heatmap (front view, X/Z axes)]
) <heatmap-front>

#figure(
  image("assets/heatmap_side.png", width: 80%),
  caption: [2D accessibility heatmap (side view, Y/Z axes)]
) <heatmap-side>

Finally, I combined all the results and displayed the average accessibility of each point on the duck, to see whether some areas were generally harder to reach than others, as shown in @duck. Red points are areas that were never reached in any of the tests.

#figure(
  grid(
    columns: (1fr,) * 3,
    image("assets/duck_right.png"),
    image("assets/duck_front.png"),
    image("assets/duck_back.png"),
  ),
  caption: [Accessibility of points on the duck's surface]
) <duck>

= Conclusion

The results are not very surprising and correspond pretty well to our prior assumptions.
We can se in @heatmap-top and @heatmap-side for example that putting duck close to the back side of the workspace greatly reduces the accessibility. @heatmap-top also indicates that a diagonal placement, that is, slightly in front and on the side of the arm seems to maximize the over reachability.

Height does not seem to affect the results much, although a slight increase in reachability can be noted for higher Z values in @heatmap-side (larger Z values are towards the bottom of the heatmap).

Finally, our assumptions about the accessibility of the various surface areas was also confirmed by @duck, although the neck parts appeared to be more accessible than we thought.

In conclusion, there doesn't appear to be one specific area that highly maximizes the reachability of the duck, and our initial intuitions were confirmed. I decided that a more thorough numerical analysis was not required, since the current placement already seemed good enough for our requirements.