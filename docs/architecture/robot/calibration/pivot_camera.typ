#set page(
  width: 21cm,
  height: 29.7cm,
  margin: 2.5cm,
  number-align: center,
  numbering: "- 1/1 -"
)

#set text(lang: "fr")
#set par(justify: true)
#set list(indent: 2em)
#set enum(indent: 2em)

#align(center)[
  = Analyse comparative des méthodes de calibration TCP pour robots

  #datetime.today().display()
]

#v(2em)

#align(center)[*Résumé*]

La calibration d’un robot est essentielle pour garantir la précision de ses mouvements.  
Deux méthodes courantes sont la *calibration pivot* et la *calibration par caméra*.  
Ce rapport présente séparément chacune de ces méthodes, analyse leurs avantages et limites, puis propose une comparaison synthétique permettant de comprendre pourquoi la calibration pivot est souvent privilégiée.

#v(2em)

#outline()

#pagebreak()

#set heading(numbering: "1.")
#counter(heading).update(0)

= Introduction

== Contexte

Le présent travail s’inscrit dans le cadre du projet *Duckify*, dont l’objectif est de permettre à un robot manipulateur de dessiner automatiquement, à l’aide d’un stylo, un motif généré par intelligence artificielle sur la surface d’un canard en plastique tridimensionnel.  
Le processus complet comprend la génération de l’image, la conversion en trajectoires exploitables par le robot, la préparation du canard et du système de prise du stylo, ainsi que l’exécution précise du dessin sur une surface courbe et irrégulière.

Dans ce contexte, la calibration du TCP (Tool Center Point) est une étape critique.  
En effet, la pointe du stylo doit être positionnée avec une grande précision pour garantir :

- la cohérence entre les trajectoires générées et le dessin réel,  
- la continuité des traits sur une surface non plane,  
- la répétabilité lors des changements de couleur ou de stylo,  
- l’absence de collisions avec la géométrie du canard.

Le projet impose également plusieurs contraintes pratiques :  
l’espace de travail est restreint, l’éclairage peut varier, et le système doit rester simple à mettre en œuvre pour permettre des itérations rapides.  
Ces contraintes rendent nécessaire l’évaluation de différentes méthodes de calibration TCP afin d’identifier celle qui offre le meilleur compromis entre précision, robustesse et facilité d’utilisation.

C’est dans ce cadre que les deux approches étudiées - la calibration pivot et la calibration par caméra - sont comparées dans ce rapport.


== Principe général

La précision d’un robot dépend fortement de la qualité de sa calibration, c’est‑à‑dire de la capacité à déterminer avec exactitude la position et l’orientation de son outil dans l’espace.  
Dans les environnements industriels, cette étape est cruciale pour assurer la répétabilité, la sécurité et la performance des opérations automatisées.

Parmi les nombreuses approches existantes, deux méthodes sont particulièrement répandues :

- la *calibration pivot*, qui repose uniquement sur la cinématique interne du robot ;
- la *calibration par caméra*, qui utilise un système de vision externe pour observer un marqueur fixé au robot.

Ces deux méthodes poursuivent le même objectif, mais diffèrent profondément en termes de mise en œuvre, de contraintes matérielles, de robustesse et de précision.  
L’objectif de ce rapport est de présenter chacune d’elles de manière indépendante, puis d’en proposer une analyse comparative permettant d’identifier leurs domaines d’application privilégiés.

#pagebreak()

= Méthode 1 : Calibration pivot

== Principe
La calibration pivot consiste à fixer un outil ou un marqueur au robot, puis à effectuer une série de mouvements autour d’un point fixe.  
En exploitant uniquement les données internes du robot (encodeurs, cinématique directe), on détermine la position exacte de ce point dans le repère du robot.

== Avantages
- Ne nécessite aucun équipement externe.  
- Fonctionne dans des environnements difficiles (mauvais éclairage, reflets, encombrement).  
- Mise en œuvre simple et rapide.  
- Très bonne répétabilité grâce à la stabilité de la cinématique interne.  
- Peu de sources d’erreur externes.

== Limites
- Suppose que la cinématique du robot est correctement modélisée.  
- Nécessite un point pivot réellement fixe et bien monté.  
- Ne permet pas de corriger des erreurs globales de positionnement dans un repère externe.

= Méthode 2 : Calibration par caméra

== Principe
La calibration par caméra utilise un système de vision externe pour observer un marqueur ou un outil fixé au robot.  
La position du robot est estimée en combinant les mesures visuelles et la géométrie du système de vision.

== Avantages
- Permet d’obtenir une calibration dans un repère externe.  
- Utile lorsque le robot doit interagir avec des objets détectés visuellement.  
- Peut corriger des erreurs globales de positionnement.

== Limites
- Dépend fortement de la qualité du système de vision.  
- Sensible aux variations d’éclairage, aux occlusions et au bruit visuel.  
- Nécessite une calibration préalable de la caméra (lentilles, distorsion, position).  
- Mise en place plus complexe et plus coûteuse.  
- Moins robuste dans des environnements industriels dynamiques.

#pagebreak()

= Analyse comparative

Avant de déterminer quelle méthode est la plus adaptée à notre cas d’utilisation, il est utile de comparer directement la calibration pivot et la calibration par caméra selon plusieurs critères techniques et pratiques. Le tableau suivant synthétise les différences essentielles entre les deux approches.

== Tableau comparatif

#table(
  columns: 3,
  align: left,
  inset: 6pt,
  stroke: 0.5pt,
  table.header(
    [*Critère*],
    [*Calibration pivot*],
    [*Calibration par caméra*]
  ),
  
    "Dépendance à l’environnement",
    "Faible",
    "Forte",
    "Besoin en matériel externe",
    "Aucun",
    "Caméra + support",
    "Complexité de mise en œuvre",
    "Faible",
    "Élevée",
    "Sensibilité aux perturbations",
    "Très faible",
    "Forte",
    "Précision interne",
    "Excellente",
    "Variable selon la vision",
    "Coût",
    "Très faible",
    "Plus élevé",
    "Adaptée aux environnements industriels",
    "Oui",
    "Souvent non",
    "Calibration dans un repère externe",
    "Non",
    "Oui",
)

== Résultat
La calibration pivot se distingue par sa *simplicité*, sa *robustesse* et sa *répétabilité*.  
Elle est particulièrement adaptée aux environnements industriels où les conditions visuelles ne sont pas maîtrisées.

La calibration par caméra, bien que plus flexible pour des applications nécessitant un repère externe, souffre de nombreuses sources d’erreur et d’une mise en œuvre plus lourde.


= Conclusion

La calibration pivot apparaît comme la méthode la plus fiable et la plus pratique pour la majorité des applications robotiques.  
Son indépendance vis‑à‑vis de l’environnement, sa facilité d’utilisation et sa précision interne en font une solution privilégiée dans les contextes industriels.  
La calibration par caméra reste pertinente lorsque l’on souhaite intégrer le robot dans un repère visuel externe, mais elle impose des contraintes techniques et matérielles importantes.

En résumé, la calibration pivot constitue la solution la plus adaptée pour notre cas d'utilisation, tandis que la calibration par caméra n'apporte rien de pertinent.