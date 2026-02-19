#set text(font: "Source Sans Pro")

#align(
  center,
  text(size: 2em, weight: "bold")[General overview of the tracing process]
)

= Tasks
- Wrapping textures (UV)
- Normals
- Generate strokes


= Inputs
- 3D model (e.g. .obj)
- Design:
  - 1st: vector pattern textures with color labels (e.g. SVG)
  - 2nd: colored pattern textures
  - 3rd: raster image + vectorization
  - 4th: front/side images

= Outputs
- List of strokes:
  - 3D positions (start + end)
  - normal vector
  - color ID

= Steps
+ (Texture Projection)

+ Color separation
  - 1st: multiple input textures, by color
  - later: color isolation and approximation

+ Topological separation
  - Color islands

+ Contour & filling
  - Contour segmentation $->$ longer strokes
  - Filling segmentation $->$ many little parallel strokes (TBD: what kind of pattern, topological optimization)
  - Position interpolation to compute 3D positions of texture points
  - Path segmentation according to normals (e.g. delta threshold)

+ Ordering
  - Sort little paths to minimize distance between consecutive end- and start-points, as well as normal delta (graph)

+ Output
  - Aggregate coordinates with color and normals
  - Format data for next step



= Questions
- one long stroke or multiple little strokes ? what is best and why ?
- should we take into consideration the size of the pen tip, especially for filling ?
- what should WE optimize ?
- what kind of filling patterns ? should they be optimized relative to the local topology ? how ?
