#import "@preview/codly:1.3.0": codly-init

#show: codly-init
#show link: set text(fill: blue)
#set text(font: "Source Sans 3")
#set heading(numbering: "1.1")

#align(center)[
  #block(inset: 2em)[
    #text(size: 20pt, weight: "bold")[Duck Reachability Analysis] \
    #v(0.5em)
    #text(size: 12pt, style: "italic")[Cone Search Optimization & Specifications]
    #linebreak()
    #v(0.3em)
    #text(size: 10pt)[Nathan Antonietti]
    #linebreak()
    #text(size: 8pt, fill: gray)[Made using Gemini]
  ]
]

#v(2em)
#line(length: 100%, stroke: 0.5pt + gray)

#v(2em)

= Overview

Determine which points on a duck surface are reachable by the UR3e robot while maintaining drawing orientation constraints. This analysis decomposes the problem, identifies constraints, explores optimizations, and establishes specifications.

= Problem Components

- *Geometric Reachability*: Which Cartesian points can the TCP reach (workspace + kinematics)
- *Orientation Feasibility*: Valid tool orientations aligned with surface normals (±25° cone)
- *Collision Avoidance*: Self-collision and obstacle detection with safety margins
- *Surface Sampling*: Uniform point distribution with normal extraction from STL mesh

= Constraints

#block(fill: rgb("f0f0f0"), inset: 1em, radius: 0.5em)[
  *Technological:*
  - Max reach: 0.85 m; Joint limits: ±π rad; Up to 8 IK solutions per pose
  - Collision detection: ~8000+ checks for 1000 points × 8 solutions
  - Orientation tolerance: ±25° cone search (DRAWING_ANGLE config)

  *Environmental:*
  - Workspace bounds: Y ≤ -0.15 m, Z ∈ [0.05, 0.50] m, radial ≤ 0.85 m
  - Duck: ~2000 mm² surface, millimeter-scale STL (0.001 scaling)
  - Non-accessible: flat base (Z < 1 mm), hidden back (Y < 0)

  *Operational:*
  - Tool must align with surface normal ±25°
  - Zero self-collisions; 0.01 m obstacle clearance
  - Real-time path planning for interactive use
]

#pagebreak()

= Functional Requirements

#table(
  columns: (1fr, 2fr),
  inset: 10pt,
  align: horizon,
  table.header(
    [*Requirement*], [*Description*],
  ),
  [Surface Sampling], [STL mesh → point cloud with normals (1–5 points/cm², ±5° accuracy, filter base & hidden regions)],
  [Transformation], [Duck placement → homogeneous transform matrix (±2 mm translation, ±2° rotation)],
  [IK + Cone Search], [Target TCP → valid joint config (max_angle=25°, cone_step=5°, prefer qnear)],
  [Collision Check], [Joint config → valid/invalid + reason (self-collision, obstacle, Z-min constraints)],
  [Reachability Map], [Batch process 100–5000 points, report success rate & per-point failures],
  [Visualization], [Interactive 3D with reachability overlay (green=reachable, red=unreachable)],
)

= Performance Targets

#figure(
  table(
    columns: (1.5fr, 1fr, 1.5fr),
    [*Metric*], [*Target*], [*Rationale*],
    [Single-point validation], [$< 50 m s$], [Real-time interaction],
    [100-point batch], [$< 10 s$], [Quick testing],
    [1000-point full scan], [$< 2 min$], [Practical analysis],
    [IK success rate], [$> 95\%$], [Few false negatives],
    [Collision accuracy], [$100\%$ @ 0.01 m], [Safety critical],
  ),
  caption: [Performance Targets]
)

= Non-Functional Requirements

- *Code Quality*: Return (success: bool, reason: str, metadata: dict); comprehensive logging; type hints
- *Configurability*: `max_cone_angle`, `cone_step`, collision margins, workspace bounds, sample density
- *Debugging*: Detailed rejection reasons; PyBullet GUI option; exportable reachability JSON
- *Robustness*: Handle missing STL files, PyBullet disconnections, variable IK solvers, bounds checks

= API Contract

```python
ok, q, reason, tcp_adjusted = checker.validate_tcp(
    robot=RobotControl, tcp=TCP6D, qnear=Optional[list],
    margin=float, check_obstacle=bool, orientation_search=bool,
    max_cone_angle=float, cone_step=float
) → Tuple[bool, Optional[list], str, TCP6D]
```

Returns: Joint angles (if ok), diagnostic reason, optionally adjusted TCP

= Success Criteria

1. Accuracy: ≥95% agreement with real-world validation
2. Performance: 1000-point scan in < 90 seconds
3. Usability: Clear visualization of feasible drawing strokes
4. Reliability: Zero collisions during executed trajectories
5. Debuggability: Clear logging and visualization for failures

= Conclusion

The UR3e duck-drawing reachability problem spans kinematics, collision detection, orientation planning, and surface geometry. By decomposing the problem systematically and implementing the specified algorithms, we build a robust validation system enabling safe, efficient collaborative robot drawing.
