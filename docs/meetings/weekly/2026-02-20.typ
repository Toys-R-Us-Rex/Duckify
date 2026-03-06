#import "@preview/suiji:0.5.1": *
#import "./template.typ": meeting, team

#show: meeting.with(
  date: datetime(year: 2026, month: 2, day: 20),
  time: [10h00],
  scribe: ("J", "L")
)

#set text(lang: "en")

= Critics received :

== General

=== Presentation

- Transform the flowchart diagram to a more transversal one
- When defining milestones, always have precise validation criteria
- Link work presented directly with milestones list
- Have local conclusions for each team part
- Continue to always display findings with tests results
- Add bullet points to slides, to help coming back in the future
- When presenting milestones, always with visual DONE/TODO
  - if still in TODO then also add the blockers
- Always present existing sources of a displayed information

=== Organization
- a locally flat duck will help for the coloring part (in prototype)
- when testing something - push up to 5-10 cases to be able to quantify complexity
- arguing about "what we will produce/not produce" is only a client's privilege
- being an expert able to manipulate the client
- Be careful that tasks don't overlap each others (e.g. research conducted by GenAI and Tracing teams)
- Pen type must be ASAP steps
- Define the interfaces
- Define the robot solution (e.g. know which move type command will suffice )

=== Research tips
- use a promise paper's reference in Google scholar to find recent development in the field

== Team focused

=== GenAI
- the client prompt could be internally updated before being send to generative model
- Try more realist model in generation tests
- Synthetise state of research results

=== Tracing
- limiting the color panel and/or patterns
- discretization : attention to contiguous zone size : not smaller than the pen tip

=== robot
- Add a visual about the simulation's environment and robot environment
- Add a visual (disc into disc) about the robot range

