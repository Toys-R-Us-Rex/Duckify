#import "./template.typ": meeting, attendees, team

#show: meeting.with(
  date: datetime(year: 2026, month: 2, day: 19)
)

#attendees()

*Location*: 23N216 | *Time*: 9h00 | *Scribe*: Jeremy

= Work done/todo

=== Marco : 
- done: 
  - recherche modèle diffusion pour génération texture + communication avec team mapping pour besoin 
- todo: 
  - continuer les recherches

=== Kevin : 
- done: 
  - recherche modèle diffusion pour génération texture
- issues: 
  - problèmes de compatibilité de librairies. Les solutions testées date souvent des années 2022-23.
- todo : 
  - continuer les recherches

== Louis :
- done: 
  - mise en place de la github policy
  - milestone des de planifications des étapes algorithmiques
  - mail envoyé au CTO pour questions au CEO 
- todo : 
  - rajout de documentation dans le git
  - update/cleaning jira
  - travailler en collaboration avec Jeremy sur le milestone restant de la team Tracing

== Jeremy :
- done :
  - recherche sur le milestone de projection de texture par LLM 
- todo: 
  - rédaction du rapport meeting
  - poursuite des recherches

== Pierre-Yves : 
- done: 
  - faire tourner logiciel de simulation sur son laptop
  - fait un wrapper pour résoudre le problème de compatibilités de librairies
  
- issues: librairies python qui fonctionnent avec le robot ne sont pas compatible avec l'environnement de simulation 
- todo : 
  - faire un déplacement A-B dans le simulateur
  - test avec le robot cette après-midi

== Cédric : 
- done: 
  - faire tourner logiciel de simulation sur son laptop
  - fait un notebook/exemple plus explicatif que ce qui était fourni du simulateur
  - Travail sur la calibration par caméra
- todo: 
  - finir notebook explicatif
  - poursuivre la calibration Hand-Eye

== Nathan :
- done: 
  - faire tourner logiciel de simulation sur son laptop

- todo:  
  - faire un déplacement A-B dans le simulateur
  - test avec le robot cette après-midi

== Alex : 
- done: 
  - ébauche des supports
- issues: 
- impossibilité de modifier un .obj sur le logiciel de modélisation 

- todo:
  - solution à l'issue avec une librairie trouvée à tester 
  - va avec la team robot au labo pour prendre mesure 
  - faire un assemblage support + modèle

== Besoins : 
- adapteur ethernet pour la team robot

== Missions : 
- à tous mettre les tâches sur Jira

== Questions :
- heure meeting vendredi matin ?
