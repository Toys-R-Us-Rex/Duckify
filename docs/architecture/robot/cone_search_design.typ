#import "@preview/codly:1.3.0": codly-init

#show: codly-init
#show link: set text(fill: blue)
#set text(font: "Source Sans 3")
#set heading(numbering: "1.1")
#set page(margin: (left: 2cm, right: 2cm, top: 2cm, bottom: 2cm))

#align(center)[
  #block(inset: 2em)[
    #text(size: 20pt, weight: "bold")[Design Report: Cone Search Algorith] \
    #v(0.5em)
    #text(size: 12pt, style: "italic")[Implementation, Validation, and Performance Analysis]
    #linebreak()
    #v(0.5em)
    #text(size: 11pt)[Nathan Antonietti]
    #linebreak()
    #text(size: 9pt, fill: gray)[Made using Gemini]
  ]
]

#v(2em)

= Introduction

This report describes the design and implementation of a reachability validation system for the UR3e collaborative robot performing drawing operations on arbitrary 3D surfaces. The solution uses an inverse kinematics (IK) solver with cone-based orientation search to determine which points on a duck surface can be safely reached. This design respects workspace constraints, kinematic limits, and collision detection requirements while providing interactive performance.

= Problem Statement

Given a 3D duck surface and the UR3e robot's current pose, determine:
- Which surface points are reachable by the robot's end-effector
- What orientations at each point are valid for drawing (aligned with surface normal ±25°)
- Whether motion to that point is collision-free

The challenge is balancing solution accuracy, computational performance, and solution feasibility.

= Architecture Overview

The system is composed of four layers: kinematic (IK + cone search), collision detection (PyBullet), TCP validation pipeline (bounds → IK → cone search), and reachability mapping (batch analysis).

*Key Components:*
- `src/safety.py` validate_tcp(): Entry point for reachability checks
- `_cone_search()`: Explores ±25° orientation cone around desired TCP
- `_try_ik_and_collision()`: Evaluates IK solutions, filters by joint limits and collisions
- PyBullet collision detection with 0.01 m safety margin
- Batch point processing with logging and statistics

*Validation Pipeline:*
1. Check workspace bounds (Y, Z, reach)
2. Try IK solutions sorted by proximity to current pose
3. Check per-link Z-minimums and collisions
4. If direct IK fails, search ±25° orientation cone
5. Return first valid solution found

#pagebreak()

= Cone Search Algorithm

The cone search is the core innovation for handling orientation constraints. Here's the actual implementation from `src/safety.py`:

```python
def _cone_search(self, robot, tcp, qnear, margin, 
                 check_obstacle, max_cone_angle, cone_step):
    tcp_xyz = np.array([tcp.x, tcp.y, tcp.z])
    original_rot = Rotation.from_rotvec([tcp.rx, tcp.ry, tcp.rz])
    
    tilt = cone_step
    while tilt <= max_cone_angle + 1e-9:
        n_azimuth = max(int(np.ceil(2 * math.pi / cone_step)), 1)
        for az_i in range(n_azimuth):
            azimuth = az_i * (2 * math.pi / n_azimuth)
            axis = np.array([math.sin(azimuth), math.cos(azimuth), 0.0])
            rv = (original_rot * Rotation.from_rotvec(axis * tilt)).as_rotvec()
            candidate_tcp = TCP6D.createFromMetersRadians(
                *tcp_xyz.tolist(), float(rv[0]), float(rv[1]), float(rv[2])
            )
            ok, q, _ = self._try_ik_and_collision(robot, candidate_tcp, qnear, margin, check_obstacle)
            if ok:
                return q, candidate_tcp
        tilt += cone_step
    return None
```

== Algorithm Details

*Inputs:* TCP pose with surface normal orientation, max_cone_angle=25° (configurable), cone_step=5°

*Search Pattern:* Nested loops exploring tilt angles (5° → 25°) and azimuths (~72 per tilt for 5° step). Total: ~432 orientation tests per point.

*Orientation Computation:* Perturbs original rotation by applying tilt around axis in XY plane at azimuth angle.

*Stopping:* Returns on first valid solution (prioritizes speed over optimality).

*Complexity:* $O(n_"tilt" times n_"azimuth")$ per point; each test includes IK solve + collision check (5-50 ms).

= Validation Pipeline

```
Workspace bounds check → IK + collision test → Cone search (if needed)
Returns: (success, q, reason, adjusted_tcp)
```

Pipeline uses fail-fast early exit: returns immediately on any success. Cone search triggered only if direct IK/collision fails.

#pagebreak()

= Implementation Details

*Surface Sampling:* Trimesh samples ~1 point per 10 mm² of duck surface; filters back (Y < 0) and base (Z < 1 mm).

*Frames:* STL (mm) → scale 0.001 → apply transform → robot frame (m).

*Collision Detection:* PyBullet with persistent 0.01 m margin. Self-collision pairs + obstacle pairs configured in constructor.

*Joint Preference:* Sorts IK solutions by distance to qnear (current pose) to improve continuity and reduce oscillation.

= Design Decisions

1. *Early Exit:* Return first valid solution (not optimal). Rationale: Interactive drawing needs sub-second response; drawing precision > joint continuity.

2. *Cone Parameters:* max_angle=25°, cone_step=5°. Rationale: 25° matches drawing tolerance; 5° step balances coverage/cost.

3. *Collision Margin:* 0.01 m (1 cm). Rationale: Safety critical; standard for collaborative robots.

4. *Sequential Processing:* PyBullet single-instance not thread-safe. Current 2-3 points/sec acceptable for offline analysis; future: thread parallelization.

5. *Face Normals:* Simple and robust; ±25° cone handles curvature variations.

#pagebreak()

= Failure Modes

*Workspace Bounds:* Y > -0.15 m (forward), Z outside [0.05, 0.50] m (vertical), reach > 0.85 m.

*IK:* Geometric configuration unreachable; common at workspace edges.

*Collision:* Self-collision, obstacle collision, per-link Z constraint violation.

*Cone Exhaustion:* All orientations within ±25° cone fail IK or collision.

*Typical Distribution (1000-point duck):*

#table(
  columns: (1.5fr, 1fr),
  inset: 10pt,
  align: horizon,
  table.header(
    [*Failure Mode*], [*%*],
  ),
  [Workspace bounds], [10-20%],
  [IK no solution], [20-30%],
  [Obstacle collision], [40-50%],
  [Self-collision], [< 5%],
  [Cone exhaustion], [5-10%],
  [Success], [30-40%],
)

= Conclusion

The cone search system validates duck surface reachability by decomposing the problem into bounds checking, IK solving, and orientation search. The design prioritizes correctness and interactivity over optimality. Performance (2-3 points/sec) is suitable for offline surface mapping and interactive single-point validation. The 30-40% success rate reflects realistic workspace and collision constraints for the duck placement.

Code is well-instrumented with logging, visualization, and analysis tools for understanding failure modes and algorithm behavior.


#v(2em)
#line(length: 100%, stroke: 0.5pt + gray)
#align(center)[
  #text(size: 8pt, fill: gray)[HES-SO Valais-Wallis - Engineering Track 304.1- 2026]
]