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
  = Transformation de coordonnées entre repère objet et repère robot
  
  #datetime.today().display()
]

#v(2em)

#align(center)[*Résumé*]

Ce rapport traite de la problématique de conversion de coordonnées entre un repère local associé à un objet et le repère global utilisé par un système robotique.
Pour établir cette correspondance, une méthode d’estimation de la transformation affine est présentée. Elle s’appuie sur un ensemble de points homologues mesurés dans les deux repères et sur une résolution par moindres carrés.

Le document aborde également une procédure permettant de convertir une normale en une orientation exploitable par le robot, afin d’assurer une manipulation cohérente de l’objet dans l’espace.

#v(2em)

#outline()

#pagebreak()

#set heading(numbering: "1.")
#counter(heading).update(0)

= Introduction

Dans de nombreuses applications, les coordonnées d’un objet sont exprimées dans un repère propre à cet objet.  
Cependant, les mouvements du robot sont définis dans un repère global différent.

Afin de permettre l'interaction entre ces deux systèmes, il est nécessaire de déterminer une transformation permettant de convertir les coordonnées d’un repère vers l’autre.

Cette transformation permet par exemple :

- d’exécuter des trajectoires définies dans le repère de l’objet
- d’utiliser des données provenant de capteurs ou de modèles 3D
- d’adapter automatiquement la position d’un objet dans l’espace

= Principe général

La transformation entre deux repères tridimensionnels peut être décrite par une transformation affine :

$
T = mat(
  R, t;
  0, 1,
)
$

où :

- $"R"$ est la matrice de rotation
- $"t"$ est le vecteur de translation

Cette matrice permet de convertir un point $"p_A"$ exprimé dans le repère objet en un point $"p_B"$ dans le repère robot :

$
p_B = T p_A
$

= Collecte des points

Pour estimer la transformation, il est nécessaire de disposer d’un ensemble de points correspondants dans les deux repères.

Chaque point est mesuré :

- dans le repère objet
- dans le repère robot

Un minimum de trois points non colinéaires est nécessaire pour déterminer une transformation.

Cependant, l’utilisation d’un nombre plus élevé de points permet d’obtenir une solution plus robuste en utilisant une résolution par moindres carrés.

Les données collectées sont donc de la forme :

$
A_i = (x_i, y_i, z_i)
$

$
B_i = (x_i', y_i', z_i')
$

#pagebreak()

= Calcul de la transformation

La transformation recherchée doit satisfaire :

$
B = R A + t
$

Afin de résoudre ce problème, on construit une matrice :

$
P = mat(
  x_1, y_1, z_1, 1;
  x_2, y_2, z_2, 1;
  dots.v, dots.v, dots.v, dots.v,
)
$

Le problème devient alors :

$
P X = B
$

où :

$
X = mat(
  R^T;
  t,
)
$

La solution est obtenue par moindres carrés :

$
X = (P^T P)^{-1} P^T B
$

La matrice de transformation finale est ensuite reconstruite sous la forme :

$
T = mat(
  R, t;
  0, 1,
)
$

= Transformation des normales

Lorsqu’un point possède également une normale de surface, celle-ci doit être transformée correctement.

Contrairement aux positions, les normales ne doivent pas être transformées directement par la matrice $"R"$.

La transformation correcte est :

$
n' = (R^{-1})^T n
$

Cette opération correspond à la transformation des vecteurs normaux sous une transformation affine.

#pagebreak()

= Conversion des normales en orientation

Dans certaines applications, la normale d’une surface doit être convertie en orientation utilisable par le robot.

== Conversion d’une normale en angles d’Euler

Soit la normale unitaire $"n = (n_x, n_y, n_z)"$ avec $"||n|| = 1"$.

On cherche des angles d’Euler $"(α, β, γ)"$ dans la convention Yaw–Pitch–Roll $(Z, Y, X)$ tels que :

$
R = R_z(α) R_y(β) R_x(γ)
$

avec par exemple :

$
R_z(α) = mat(
  cos(α), -sin(α), 0;
  sin(α),  cos(α), 0;
  0,       0,      1,
)
$

$
R_y(β) = mat(
  cos(β), 0, sin(β);
  0,      1, 0;
  -sin(β), 0, cos(β),
)
$

$
R_x(γ) = mat(
  1, 0,        0;
  0, cos(γ), -sin(γ);
  0, sin(γ),  cos(γ),
)
$

On aligne l’axe canonique $"e_z = (0, 0, 1)"$ avec $"n"$ :

$
R_z(α) R_y(β) mat(0; 0; 1)
  = mat(
    sin(β) cos(α);
    sin(β) sin(α);
    cos(β),
  )
$

En identifiant ce vecteur à $"n"$, on obtient :

$
n_x = sin(β) cos(α), "\quad"
n_y = sin(β) sin(α), "\quad"
n_z = cos(β)
$

D’où :

$
β = arctan 2(sqrt(n_x^2 + n_y^2), n_z)
$

$
α = arctan 2(n_y, n_x)
$

Le troisième angle $"γ"$ (roll) représente une rotation autour de la normale elle-même.  
On peut choisir :

$
γ = 0
$

La rotation minimale qui aligne $"e_z"$ avec $"n"$ est alors :

$
R = R_z(α) R_y(β)
$

#pagebreak()

== Conversion d’une normale en vecteur de rotation

Une autre représentation des orientations consiste à utiliser un vecteur de rotation.

Une rotation est décrite par :

- un axe de rotation unitaire $"k"$
- un angle de rotation $"θ"$

Le vecteur de rotation est :

$
r = θ k
$

Pour aligner l’axe $"Z"$ avec la normale $"n = (x, y, z)"$ :

$
θ = arccos(z)
$

L’axe de rotation est le produit vectoriel entre $"Z"$ et $"n"$ :

$
Z = mat(0; 0; 1)
$

$
k = Z × n
$

soit :

$
k = mat(
  -y;
  x;
  0,
)
$

Après normalisation :

$
k = 1 / sqrt(x^2 + y^2) · mat(
  -y;
  x;
  0,
)
$

Le vecteur de rotation final est :

$
r = θ · mat(
  -y / sqrt(x^2 + y^2);
   x / sqrt(x^2 + y^2);
   0,
)
$

== Comparaison des méthodes


#grid(
  columns: (1fr, 1fr),
  rows: (auto, auto),
  grid.cell(
  figure(
    image("Euler_angle.png", width:45%),
    caption: [Angle d'Euler],
  )),
  grid.cell(
    figure(
      image("Rotation_vector.png", width:49%),
      caption: [Vecteur de rotation],
  ))
)

Une normale définit uniquement une direction dans l’espace et ne fournit qu’une contrainte partielle sur l’orientation.

La conversion en angles d’Euler nécessite trois rotations indépendantes.  
Dans l’approche précédente, la rotation autour de l’axe $"Z"$ est fixée arbitrairement :

$
r_z = 0
$

La représentation par vecteur de rotation :

- décrit une rotation minimale entre deux directions  
- évite des hypothèses arbitraires  
- correspond à la représentation utilisée par le robot  

= Implémentation

Algorithme :

1. Mesurer les points de référence dans l’espace de l’objet et dans l’espace du robot  
2. Calculer la matrice de transformation pour passer d’un espace à l’autre  
3. Transformer les coordonnées de l’espace de l’objet dans celui du robot  
4. Convertir la normale en vecteur de rotation  
= Conclusion

La transformation entre repère objet et repère robot constitue une étape fondamentale pour l’intégration de données provenant de différentes sources.

La méthode présentée permet d’estimer efficacement cette transformation à partir d’un ensemble de correspondances de points.

L’utilisation des vecteurs de rotation pour représenter l’orientation offre une solution robuste et compatible avec les systèmes robotiques modernes.

#v(2em)

// Annexes en lettres
#set heading(numbering: "A.1")
#counter(heading).update(0)

= Annexe

== Code Python

=== Calcul de la matrice de transformation

```python
def create_transformation(A, B):
    P = np.hstack([A, np.ones((N, 1))])
    X, _, _, _ = np.linalg.lstsq(P, B, rcond=None)

    R = X[:3, :].T
    t = X[3, :]

    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t

    return T
```

=== Conversion normale en vecteur de rotation

```python
def normalize(v):
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    return v / n if n > 0 else v

def normal_to_rxyz(n):
    x, y, z = normalize(n)

    theta = np.arccos(z)
    r = np.sqrt(x * x + y * y)

    rx = -theta * (y / r)
    ry =  theta * (x / r)
    rz = 0

    return np.array([rx, ry, rz])
```