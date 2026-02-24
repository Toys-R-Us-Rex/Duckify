#import "./template.typ": meeting, attendees, team

#show: meeting.with(
  date: datetime(year: 2026, month: 2, day: 23),
  location: [23N316],
  time: [9h00],
  scribe: "N"
)

- KV: 
  - Continuer milestone trouver AI adapter
  - Tester Paint-it (pas prometteur pour l'instant)
  - Accès a chacha
- MC:
  - Faire benchmark génération de canard bien ou pas
- AV: 
  - Acheté 2 feutres verts (8m & 1,5mm)
  - Discussion pièces en bois avec monsieur Darbellay
  - Imprimer un canard
  -  (A faire) Imprimer un "feutre" 3D avec bonne mesure
- JD:
  - Meeting tracing gen-ai: Weekly report, research report
  - Commence implémentation du pipeline tracing
- NA:
   - Acheté les feutres
   - Préparation de la présentation de vendredi
   - Rapport technique bras robot
- LH: 
  - Fini de setup docker (compose) pour TEXture + README
    - python avec paramètres
  - PR reviews
  - Commence (avec Jeremy) algo de tracing
  - Admin
- CM:
  - Calibration Camera à TCP
    - A tester avec le robot cette semaine
    - Besoin d'un outil pour calibration (au lieu du stylo)
- PYS:
  - Préparation présentation vendredi
  - Modification wrapper + Cleanup rapport

#line(length: 100%)

- LLM rename to "Gen-AI"
- Sprint 1 completed

- PYS:
  - Mail a Loïc pour utiliser robot demain
  - Objectif: faire dessin (forme 2D) sur une feuille

- LH:
  - Terminé sous-tâches 
  - Tâches avec estimations de temps


- Discussion Milestones de la semaine
  - robot: Redéfinir Milestones
  - Avoir canard imprimé pour la réunion avec le client (date à définir)
  - tracing: démo algo
  - Rester flexible, solutions peuvent changer
    - Prévoir potentiel cul-de-sac
  - robot: tracing envoient un point et la normale de ce point
    - Potentielle problématique avec l'angle du bras robot par rapport à la surface du canard

- Démarrage Sprint 2
