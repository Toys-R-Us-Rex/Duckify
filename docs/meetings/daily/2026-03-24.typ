#import "./template.typ": *

#show: meeting.with(
  date: datetime(year: 2026, month: 3, day: 24),
  location: [23N415],
  time: [9h05-9h40],
  scribe: "C",
)


*Kevin*

Hier:
  - Improve quality of generated images: research about FreeU
  - Finalized commit PR; Integration GenAI
Ajd:
  - Test FreeU Solution to decrease noise of generated texture
  - Fine-tuning & Generation of a custom dataset for the training phase of t2t mv-adapter

*Marco*

Show:
  - Output of the mv-adapter training: file and input/output image of the training
Hier:
  - Research on training mv-adapter (architecture), this work but we do not have a data train set big enough
Ajd:
  - Continue training on mv-adapter model

*Alexandre*

Hier:
  - Collage support canard to the woodden plaque: solve support stability issue
  - Plan the promotional site
  - Work with GenAI team for prompt engineering
Ajd:
  - Continue prompt engineering
  - Begin promotion site

*Jeremy*

Show:
  - Old and new UV map
Hier:
  - Redispatch the UV map to avoid point superposition
Ajd:
  - Create test for team robot with less points

*Louis*

Hier:
  - PR for integration interface
  - PR from GenAI for integration
  - Begin to look for integration 
Ajd:
  - Integration robot part into main branch
  - From *Alexandre*: change color selection -> use toggle on/off

*PY*

Show:
  - Graphs relating to the robotics team’s problems: large discrepancies between joint positions, resulting in significant robot movements
  - Animation computation point on PyBullet
Hier:
  - Explore and implement PyBullet planer
    - Okay in the limit of the test
Ajd:
  - Possible test on robot
  - Continue work on planer

*Nathan*

Hier:
  - Integration robot in Duckify
  - Init PR to merge robot code into the main project
  - Work on angle optimisation for pathfinding as asked by *Pierre-Yeves*
Ajd:
  - Continue angle optimisation for pathfinding

*Cédric*

Hier:
  - Added documentation and type hints
  - Review and fix robot integration PR
  - Add command line arguments to the main robot function

Ajd:
  - Improve arguments for main function

*Comment*

Retard:
  - Traffic accident delayed the start of the meeting.

Comment:
  - *Marco* to *Jeremy*: Possible axes missaligned between old and new UV map model
    - Answer: An older model is likely being used; the orientation setting needs to be changed
  - *Louis* to *PY*: What is the total lenght of the robot?
    - Answer: around 70cm