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
= Calibration de la position du Tool Center Point (TCP)

  #datetime.today().display()
]
#v(2em)

#align(center)[*Résumé*]

La précision de positionnement d’un outil dépend fortement de la connaissance exacte de sa géométrie par rapport au système mécanique qui le porte.  
Le _Tool Center Point_ (TCP) correspond au point de référence utilisé pour décrire la position réelle de l’outil dans l’espace.

Ce rapport présente une méthode de calibration du TCP basée sur la collecte de plusieurs poses autour d’un point fixe.  
Les données sont ensuite exploitées à l’aide d’une résolution par moindres carrés afin d’estimer l’offset du TCP dans le repère de la bride.  
Finalement, différentes métriques permettent de vérifier la validité des mesures ainsi que la qualité de la calibration obtenue.

La méthode de pivot utilisée permet uniquement d’estimer la position du TCP.  
L’orientation de l’outil ne peut pas être déterminée avec cette approche car aucune contrainte géométrique ne permet de l’observer.

#v(2em)
#outline()

#pagebreak()

#set heading(numbering: "1.")
#counter(heading).update(0)

= Introduction

Dans de nombreuses applications de manipulation ou d’usinage, les trajectoires sont définies par rapport à un point spécifique de l’outil.  
Ce point, appelé *Tool Center Point* (TCP), correspond généralement à l’extrémité fonctionnelle de l’outil.

La position du TCP n’est pas directement connue par le système mécanique.  
Elle doit être définie comme un décalage (*offset*) par rapport à la bride de montage de l’outil.

Une estimation incorrecte de cet offset peut entraîner :

- des erreurs de positionnement
- des trajectoires imprécises
- une mauvaise répétabilité des opérations

La calibration du TCP consiste donc à déterminer avec précision la position de ce point dans le repère de la bride.

= Définition des repères

La calibration repose sur trois repères principaux :

- repère de base
- repère de la bride (flange)
- repère outil TCP

#figure(
  image("relation_bride_tcp.png", width:70%),
  caption: [Relation entre la bride et le TCP],
)

= Principe de la calibration du TCP

La méthode utilisée repose sur une propriété géométrique simple :

#align(center)[
  *« le TCP correspond à un point fixe dans l’espace lorsque l’outil pivote autour de celui-ci. »*
]

Lors de la calibration, l’extrémité de l’outil est maintenue sur un point fixe tandis que l’orientation (angle d'approche) du système change.

Chaque mesure fournit :

- la position de la bride
- son orientation

Ces informations permettent de reconstruire la position du TCP par rapport à la bride.

= Collecte des données

== Principe

La calibration nécessite plusieurs poses différentes autour du même point pivot.

Chaque pose est représentée par :

$
[x, y, z, r_x, r_y, r_z]
$


- $(x, y, z)$ représente la position de la bride
- $(r_x, r_y, r_z)$ représente le vecteur rotation (axis-angle)

Ces valeurs permettent de reconstruire la transformation homogène :

$
T = mat(
  R, p;
  0, 1,
)
$

avec :

- $R$ la matrice de rotation
- $p$ le vecteur de translation

== Procédure

La collecte des données se déroule selon les étapes suivantes :

1. placer la pointe de l’outil sur un point fixe  
2. modifier l’orientation du système  
3. enregistrer la pose  
4. répéter l’opération plusieurs fois  

Un minimum de six poses est nécessaire afin d’obtenir une solution stable, mais un nombre plus élevé de mesures améliore la robustesse du calcul.

= Validation des données collectées

Avant d'effectuer la calibration, il est important de vérifier la qualité des mesures.

== Cohérence du point pivot

À partir d’un TCP de référence $r = [x, y, z]$ (par exemple issu d’une ancienne calibration), on peut estimer la position du point pivot dans le repère global :

$
c_i = p_i + R_i r
$

avec :

- $R_i$ la matrice de rotation
- $p_i$ le vecteur de translation
- $c_i$ la position TCP théorique

Si les mesures sont cohérentes, les points $c_i$ doivent être très proches les uns des autres.

La dispersion est définie par :

$
"spread" = max(||c_i - bar(c)||)
$

où $bar(c)$ désigne la moyenne des $c_i$.

Une faible valeur indique que les mesures sont compatibles avec l’hypothèse d’un point fixe.

== Amplitude du mouvement

Pour éviter un problème mal conditionné, la bride doit avoir suffisamment bougé :

$
"motion" = max(||p_i - p_0||)
$

== Variation d’orientation

Une variation importante d’orientation améliore la précision de la calibration.

L’angle de rotation peut être estimé à partir de la trace de la matrice de rotation :

$
θ_i = arccos(("trace"(R_i) - 1) / 2)
$

et la variation totale :

$
Δ θ = max(θ_i) - min(θ_i)
$

= Calcul du TCP

Le TCP est défini comme un vecteur $t$ dans le repère de la bride.

Pour chaque mesure :

$
c = p_i + R_i t
$

où $c$ correspond au point pivot dans le repère global.

Cette relation peut être réécrite :

$
R_i t - c = -p_i
$

En empilant toutes les équations on obtient :

$
A x = b
$

avec :

$
x = mat(
  t;
  c,
)
$

$
A = mat(
  R, I,
)
$

Le système est résolu par une méthode de *moindres carrés* :

$
x = (A^T A)^{-1} A^T b
$

Cette solution fournit :

- $t$ la position $[x, y, z]$ du TCP dans le repère de la bride  
- $c$ la position du point pivot dans le repère global  

#pagebreak()

= Validation de la calibration

Une fois le nouvel offset déterminé, il est nécessaire de vérifier que la calibration est correcte.

== Test de rotation

Le principe consiste à effectuer des rotations autour du TCP estimé :

- rotation autour de l’axe $x$
- rotation autour de l’axe $y$
- rotation autour de l’axe $z$

dans les deux directions.

== Observation

Si la calibration est correcte :

- le TCP reste fixe
- seule l’orientation change

Si un déplacement du point est observé, cela signifie que l’offset TCP est incorrect.

= Implémentation

Algorithme :

1. Collecter plusieurs poses  
2. Convertir les poses en matrices homogènes  
3. Construire le système linéaire  
4. Résoudre par moindres carrés  
5. Extraire l’offset TCP  
6. Valider par rotation autour du TCP  

= Conclusion

La calibration du TCP est une étape essentielle pour garantir la précision des mouvements basés sur un point outil.

La méthode présentée repose sur :

- la collecte de plusieurs poses autour d’un point fixe
- la résolution d’un système linéaire par moindres carrés
- la validation expérimentale de la calibration

Cette approche permet d’obtenir une estimation robuste du TCP tout en restant simple à mettre en œuvre.

#pagebreak()

#set heading(numbering: "A.1")
#counter(heading).update(0)

= Annexe

== Code Python

```python
import numpy as np

def calibrate_tcp(Ts):
    '''
    Ts: List of homogeneous transformation matrices representing
        the pose of the robot flange for each measurement.

    return: positional TCP offset (x,y,z)
    '''
    N = len(Ts)

    A = np.zeros((3*N,6))
    b = np.zeros((3*N))

    for i,T in enumerate(Ts):

        R = T[:3,:3]
        p = T[:3,3]

        A[3*i:3*i+3,0:3] = R
        A[3*i:3*i+3,3:6] = -np.eye(3)
        b[3*i:3*i+3] = -p

    x,_,_,_ = np.linalg.lstsq(A,b,rcond=None)

    return x[:3]
```