#import "./template.typ": meeting

#show: meeting.with(
  date: datetime(year: 2026, month: 03, day: 03),
  time: [10h30],
  scribe: "M"
)

= Presentation :

- Pres Robot: On montre les avantages du robot contre l'humain. On montre les chiffres de robot vs humain. 
- Pres AI: On montre les avantages de l'option standard et l'option plus. 
- Pres Impression 3D: On montre les 3 design de canard.

= CEO Commitments :

- Option Plus 550 CHF / Mois 
- Modèle de canard en annexe
- Bras Robot 

= CEO Inputs: 

- Nom minuscule, Temps de production de canard, Correction du PV
- Pour vendredi 06.03.2026: Envoyer la vidéo du canard au CEO

= Point pour la prochaine séance: 

- Changer de salle si possible

= CTO Inputs:

- Faire la demande formelle pour avoir un budget et un lieu ( rooftop ) pour la soirée 


=== Annexes
#align(left)[
  #figure(
    image("../assets/model3d.png", width: 30%),
    caption: [
      Modèle proposé lors de la réunion (approuvé)
    ],
  ) 
]