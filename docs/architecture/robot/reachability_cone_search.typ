#import "@preview/codly:1.3.0": codly-init

#show: codly-init
#show link: set text(fill: blue)
#set text(font: "Source Sans 3")
#set heading(numbering: "1.1")

#align(center)[
  #block(inset: 2em)[
    #text(size: 20pt, weight: "bold")[UR3e Reachability Logic and Reasoning] \
    #v(0.5em)
    #text(size: 12pt, style: "italic")[Version 2: Advanced Reachability Mapping]
    #linebreak()
    #v(0.3em)
    #text(size: 10pt)[Nathan Antonietti]
    #linebreak()
    #text(size: 8pt, fill: gray)[Made using Gemini]
  ]
]

= Purpose
This document details the second iteration of the robot reachability analysis system, focusing on the *get_reachable* logic implemented in *safety.py*. While the initial version (*is_reachable*) provided a binary feasibility check, this version implements a granular mapping of the *angular accessibility window* for any given target point on a 3D model.

= Core Algorithm: *get_reachable*
The *get_reachable* function moves beyond simple "yes/no" logic by performing a high-density sampling of approach orientations.

== Cone Sampling Strategy
To account for the 6-DOF robot's flexibility, the algorithm sweeps a cone of potential tool orientations centered on the surface normal. It employs two sampling parameters:
- *Azimuth Step*: Rotation around the normal axis (roll).
- *Tilt Step*: Angular deviation from the normal axis (tilt rings).

This creates a discrete "cloud" of orientations. For every sampled orientation, the system attempts to find a mathematical solution for the robot arm joints.

== The Multi-Stage Verification Pipeline
For each sampled orientation, the following constraints must be met:
1. *Inverse Kinematics (IK) Success*: A solution must exist within the UR3e's workspace.
2. *Joint Angle Compliance*: The resulting configuration must stay within operational limits (typically $[-2pi, 2pi]$).
3. *Collision-Free Path*: Safety is guaranteed not just at the destination, but along the approach. The algorithm uses linear joint interpolation ($q_"interp" = q_"start" + t dot (Delta q)$) to check for collisions at several steps $t$ between the current pose and the goal.

= System Evaluation
The logic is validated using complex 3D meshes (e.g., *duck.stl* with ~10,000 faces) and using a single point cone search visualization.

== Quantitative Metrics
The demo notebook samples random points across the mesh surface and computes:
- *Reachability Ratio*: The percentage of points with at least one valid approach.
- *Orientation Density*: The mean number of valid directions per point, indicating "how easy" a point is to work on.

== Interactive Visualization
Using Plotly, the system generates a 3D visualization where points are color-coded based on their accessibility density (e.g., Viridis scale). *Red dots* represent "dead zones" where no approach direction is valid, providing immediate visual feedback for cell setup.

= Global Optimization: *duck_position.ipynb*
When the reachability ratio is insufficient, the system uses a *vector-based heuristic* to optimize object placement:
1. Identify all *failed points* $p_j$ on the mesh.
2. Calculate a translation vector $bold(V)$ by averaging the vectors from each failed point towards the robot base $bold(b)$.
3. Incrementally move the object along $bold(V)$ and re-run the analysis.

This iterative approach transforms the reachability system from a passive checker into an active workspace optimizer.

#v(2em)
#line(length: 100%, stroke: 0.5pt + gray)
#align(center)[
  #text(size: 8pt, fill: gray)[HES-SO Valais-Wallis - Engineering Track 304.1 - 2026]
]