#import "@preview/lovelace:0.3.0": *

= Inputs

- 3D model
  - Vertex coordinates (3D vectors)
  - Normals (3D vectors)
  - Edges, faces
  - Texture / UV coordinates (2D vectors)
- Unwrapped texture (2D image)

= Algorithm

#pseudocode-list(hooks: .5em)[
  + $I := emptyset$
  + $S := emptyset$
  + $P := emptyset$
  + load image
  + simplify colors to available palette
  + separate colors
  + *for each* color $c$
    + identify island borders $I_c = {I_c_1, I_c_2, ..., I_c_m}$
    + $I = I union I_c$
  + *for each* island $i$
    + resample border polygon $p_i$ into segments $S_i = {S_i_1, S_i_2, ..., S_i_n}$ of length $l$
    + $S = S union S_i$
    + *for each* $f = 1, ..., k$
      + compute intersections of parallel line $L_f$ with border polygon $p_i$
      + subdivide $L_f$ into segments $F_(i,f) = {F_(i,f)_1, F_(i,f)_2, ..., F_(i,f)_h}$ of length $l$
      + $S = S union F_(i,f)$
  + *for each* segment $s_j = ({P_1(u_1, v_1), P_2(u_2, v_2)}, c)$ in $S$
    + interpolate 3D positions and normals using UV coordinates
      + $V_1(x_1, y_1, z_1), N_1(n_x_1, n_y_1, n_z_1) <- P_1(u_1, v_1)$
      + $V_2(x_2, y_2, z_2), N_2(n_x_2, n_y_2, n_z_2) <- P_2(u_2, v_2)$
    + $P = P union {(V_1, V_2, N_1, N_2, c)}$
]

= Future considerations

- Input may be a side image of the duck $->$ add a projection step at the beginning

- Output can be optimized, for example by sorting the segments to minimize distance or normal delta

- Segments may be non-linear (e.g. arcs) depending on robot interface and constraints

- Segments may need to be split when crossing sharp edges

- Other filling patterns can be implemented (e.g. concentric border, dots, waves, crosses, etc.)
