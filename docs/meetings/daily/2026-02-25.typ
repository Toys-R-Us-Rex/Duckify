#import "./template.typ": *

#show: meeting.with(
  date: datetime(year: 2026, month: 2, day: 25),
  location: [Online],
  time: [9h00],
  scribe: "A"
)

*Marco*

- Benchmark fait
- Seconde méthode autre que text to texture -> image to texture.
- Test monochrone : ok
- Test de symbole : perte de précision
- Milestone de générer un symbole : le faire à la main plutôt que par IA

*Kevin*

- Test de Painted : solution très mauvaise
- SyncMVD : aussi mauvais résultat
- MVPaint : Calypso lent + environnement => pas concluant
- Utile de continuer de chercher ? Mettre en commun avec Marco
- Bloqueur : Chacha et disco lent à mettre en place, Calypso lent (vitesse)

*Alex*
- pas de découpe laser car pas de design fini ni discussion avec M. Darbellay
- hauteur du support $->$ idée plus précise mais pas exacte
- supports des feutres plutôt bien évalués par Mme. Richard
- plutôt qu'une plaque avec des trous, utiliser les goupilles en métal à disposition
- supports canard doivent être plus robustes et plus larges
- pas de présentation aujourd'hui
- lancé impression canard arrondi $->$ arrêté à cause de problèmes
- ajd:
  - correction des supports
  - regarder avec M. Darbellay pour découpe laser

*Louis*
- Travail avec Jeremy
- Pipeline devait être complété : pas tout à fait
- Administratif : review de pull request + fermer des branches
- Branche de la team robot embêtante : à voir quoi en faire

*Jeremy*
- Pas de bloqueurs particuliers
- Continuer sur ce qui était prévu hier

*Nathan*
- Continuer sur la range du robot
- Animation sur simulation : attraper un stylo

*P-Y*

- Dessiner sur 2D : succès
- Objectif suivant : surface non-uniforme
- Dessin non-plat + 3D
- Timing short pour les milestones

*Cédric*
- Calibration TCP : mauvaises formules
- Maintenant : corrigée -> A tester
- Mise en évidence sur l'origine de la calibration

*Commentaire*

- K : Calypso "instable"
- L : Source du problème peut-être perte de paquets (MTU)
- L : Milestone 3D pas clairement défini
- P-Y : Que faire pour avoir un intégration complète
- L : Pour 15h, préparer des questions pour la réunion avec le CEO
- L : *Bien* formuler la question pour que la réponse soit utile et éviter un cul-de-sac
- L,K : Mettre en commun le code (entry point) à faire avant vendredi
- K : Intégration de la partie Gen AI vers Tracing pour que la pipeline soit complétée
- M : Pour chacha et disco, regarder la semaine prochaine
- K : Temps investi pour pas grand chose (Chacha, Disco)
- P-Y : Idée de pipeline complète à regarder après cette réunion
