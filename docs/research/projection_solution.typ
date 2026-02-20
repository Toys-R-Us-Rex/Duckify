#import "@preview/codly:1.3.0": codly-init

#show: codly-init
#show link: set text(fill: blue)
#set text(font: "New Computer Modern")
#set heading(numbering: "1.1")

#set quote(block: true)
#show quote.where(block: true): box.with(
  stroke: (left: 1pt)
)
#show quote.where(block: true): set text(fill: black.lighten(20%))

#align(
  center,
  text(size: 2em, weight: "bold")[Research report]
)

#align(
  center,
  text(size: 1.5em, weight: "bold")[Solutions for texture projection]
)

= Objective
#linebreak()
The goal of the research phase is to explore potential solutions for the texture projection problem :


#quote()[
   a way to project a texture on a 3D model, given a 2D image of the texture and a 3D model of the object and then get the UV coordinates of the projection.
]

Mutliple scenarios are considered :

+ The LLM with input [.obj and prompt describing the texture)] output a complete solution (e.g. UV coordinates + texture)
+ The LLM outputs an intermediate representation (e.g. UV coordinates) and a separate module is responsible for applying the texture on the 3D model
+ The LLM only outputs sides views of the texture and a separate module is responsible for projecting it on the 3D model

Scenario 1 is the one to focus on as it is a complete solution.

= Research
\
+ Online research showed that solutions to scenario 1 exists since few years and are commercially available. For example, Scenario's Texture#footnote(link("https://www.scenario.com/blog/ai-texture-generation")) is a web-app that can generate textures from images and apply them to 3D models. However, those web solutions are not open source nor free to use. Thus, researchs have been oriented toward a local solution that can be integrated in our pipeline is necessary.
+ A publication : TEXTure: Text-Guided Texturing of 3D Shapes#footnote(link("https://texturepaper.github.io/TEXTurePaper/")) provide potential solution. The paper describes an iterative framework leveraging a pretrained depth-to-image diffusion model to synthesize, edit, and transfer high-fidelity 3D textures. This finding is promising thus to be explored.

= TEXTure exploration
- An local analysis of the forked repo showed that possible outputs are fitting our need : 
  1. `mesh.obj` : containing the 3D model of the object with the UV coordinates corresponding to the texture projection and a section with the UV coordinates of the projection.
  2. `albedo.png` : texture image

- Next step is to test the repo in contained environment (due to librairies issues) and see if the outputs desired are possible to retrieve. The work of containerization has been done by Louis and further tests are expected to be conducted by Marco.
  

= Resources consulted

=== Fundamentals
- #link("https://en.wikipedia.org/wiki/UV_mapping")[UV Mapping and Mesh Parameterization Concepts (Wikipedia)]

=== Implementation ideas
- #link("https://stackoverflow.com/questions/4083944/opengl-texture-mapping?rq=3")[OpenGL Texture Mapping Architecture and Workflows (StackOverflow)]
- #link("https://stackoverflow.com/questions/14440455/uv-texture-mapping-in-python")[Approaches to UV Texture Mapping Implementations in Python (StackOverflow)]
- #link("https://stackoverflow.com/questions/14878467/how-to-generate-texture-mapping-images")[Algorithmic Generation of Texture Mapping Images (StackOverflow)]

=== Possible tools
- #link("https://github.com/jpcy/xatlas")[xatlas: Open-source Mesh Parameterization and UV Unwrapping Library (GitHub)]