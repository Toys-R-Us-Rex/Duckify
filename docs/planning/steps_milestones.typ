#set text(font: ("Source Sans 3", "Source Sans Pro"))

#let tag(name, fill: gray.lighten(40%)) = {
  box(
    stroke: black + 1pt,
    fill: fill,
    radius: 4pt,
    inset: (x: 6pt, y: 4pt),
    text(size: 0.8em, name)
  )
}

#show regex("[tT]est(s|ed)?"): highlight.with(fill: red)

#let mapping = tag(fill: green.lighten(60%))[Mapping]
#let printing = tag(fill: orange.lighten(30%))[3D Modeling]
#let admin = tag(fill: gray.lighten(40%))[Admin]
#let general = tag(fill: black.lighten(20%), text(fill: white)[General])
#let robot = tag(fill: blue.lighten(60%))[Robot]
#let llm = tag(fill: purple.lighten(60%))[LLM/AI]
#let interface = tag(fill: yellow.lighten(40%))[UI]


#table(
  columns: (auto, 1fr),
  inset: .4em,
  align: (center + horizon, left),
  table.header[*Week*][*Milestones*],
  [W1], [
    - #robot 
      - Assess python libraries and virtual simulator
      - Basic arm calibration with the usage of the integrated camera ($alpha$)
      - Move robot programmatically: follow instructions, move arm A $->$ B
      - Grab and release a predefined object at a predefined location. 
      - Define robot range, constraints and precision
    - #llm
      - Select and test generative AI solution to create textures from a textual prompt
      - Create a few textures (4-5) stored and labeled
    - #mapping 
      - Select unwrapping solution (projection, direct AI generation, ...)
      - Lay out algorithmic steps for generating drawing instructions from a texture
    - #printing 
      - Sketch supports, verified by expert
      - Print duck to experiment with 3D printer
    - #admin
      - Precisely define MVP (what it is / isn't) and milestones
      - Define interfaces between steps
      - Complete the milestones for the whole 7 weeks (this table)
  ],
  [W2], [
    - #mapping
      - Pipeline done : wrapped texture to 3D drawing segments
      - Texture projection process implemented (and working)
      - Define optimization scope and goal, with feedback / validation criteria
    - #printing
      - Duck supports are printed, ready to be tested
      - Sketch a 3D design that can be use to have a fixed configuration of object and tools (eventually the supports) (needed to be verified by expert)
    - #robot
      - Draw on a 2D surface (tools already set and grabbed by the robot)
      - Add supports and tools into the virtual simulation
      - Use of the camera to id and calibrate the robot relative position of the tools and object
      - Can grab and change tools and manipulate them (not drawing only hold into a initial position)
      - Draw on a 3D surface (tools already set and grabbed by the robot)
    - #llm
      - Assess generative model limits: prompt fidelity, instructions following (output format/shape)
  ],
  [W3], [
    - #mapping
      - Full pipeline done: side images to 3D drawing segments
      - Path optimization working as defined by scope and goal
    - #printing
      - Print tool support + attachments
    - #robot
      - Draw a line on a duck and switch pen
    - #general
      - *MVP / Prototype*
    - #llm
      - Generate unwrapped textures from models that respect cubic/simple-shaped duck model shape 
  ],
  [W4], [
    - #robot
      - Optimize calibration / drawing precision
      - Constant drawing pression
      - Control drawing angle
    - #interface
      - Functional interface to trigger pipeline (according to CEO's needs)
  ],
  [W5], [
    - #robot
      - Optimize calibration precision
      - Constant drawing pression
      - Control drawing angle
      
  ],
  [W6], [
    - #robot
      - Optimize drawing speed
    - #general
      - Functional product ($beta$)
  ],
  [W7], [
    - #robot
      - Reserve
  ]
)