#import "@preview/suiji:0.5.1": *
#import "./template.typ": meeting, worker-attendees, direction-attendees, team

#show: meeting.with(
  date: datetime(year: 2026, month: 2, day: 20)
)

#worker-attendees()\
#direction-attendees()

*Time*: 10h00

*Scribes :* Jeremy & Louis

= Critics received :

== General

=== Presentation

- Transform the flowchart diagramm to a more transversal one
- When defining milestones, always have precise validation criterias
- Link work presented directly with milestones list
- Have local conclusions for each team part
- Continue to always display findings with tests results
- Add bullet points to slides, to help coming back in the future
- When presenting milestones, always with visual DONE/TODO
  - if still in TODO thean aslo add the blockers
- Always present existing sources of a displayed information

=== Organisation
- a locally flat duck will help for the coloring part (in prototype)
- when testing something - push up to 5-10 cases to be able to quantify complexity
- arguing about "what we will produce/not produce" is only a client's privilege
- beeing an expert able to manupilate the client
- Be carefull that tasks don't overlap each others (e.g. research conducted by GenAI and Tracing teams)
- Pen type must be ASAP steps
- Define the interfaces
- Define the robot solution (e.g. know which move type command will suffice )

=== Research tips
- use a promise paper's reference in Google scholar to find recent development in the field

== Team focused

=== GenAI
- the client prompt could be internally updated before beeing send to generative model
- Try more realist model in generation tests
- Synthetise state of research results

=== Tracing
- limiting the color panel and/or patterns
- discretisation : attention to contigus zone size : not smaller than the pen tip

=== robot
- Add a visual about the simulation's environnement and robot environnement
- Add a visual (disc into disc) about the robot range

