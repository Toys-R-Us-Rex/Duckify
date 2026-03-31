= Exploration de MV-Adapter pour la génération de textures à partir d’une image

== Introduction

Générer des textures à partir d’une image est une des potentielles méthodes.

On explore MV-Adapter pour générer une texture sur un mesh de canard à partir d’une image de référence.

L’objectif est simple : donner une image et obtenir une texture directement utilisable.

== Pourquoi MV-Adapter

MV-Adapter permet de générer des images cohérentes entre plusieurs vues.

Il s’appuie sur des modèles de diffusion déjà entraînés comme Stable diffusion XL.

Il ajoute une cohérence multi-vues sans modifier le modèle de base.

Le problème consiste en projeter une image 2D sur un mesh 3D avec des coordonnées UV.

Le problème principal est de générer plusieurs vues cohérentes à partir d’une seule image.

== Pipeline

Le pipeline est le suivant :

1. Fournir le mesh du canard
2. Fournir une image de référence
3 Générer des vues cohérentes avec MV-Adapter
4. Reprojeter sur le mesh
5. Générer la texture finale

== Avantages

- Moins de travail manuel
- Cohérence entre les vues
- Compatible avec SDXL

Cela fonctionne bien pour des objets simples comme un canard.

== Motivation

Une démo image-to-texture existe déjà :
#link("https://huggingface.co/spaces/VAST-AI/MV-Adapter-Image2Texture")[#text(fill: blue)[Demo Img2Texture]]

Donc la méthode est déjà fonctionnelle.
Cela permet :
- de tester rapidement
- d’utiliser ses propres meshes
- de contrôler les paramètres
Le prochain step est de tester en local.

== Conclusion

MV-Adapter est adapté pour générer des textures à partir d’une image.

Il permet de garder une cohérence entre les vues.

C’est une bonne base pour créer une pipeline automatique sur le canard.

#link("https://arxiv.org/pdf/2412.03632")[#text(fill: blue)[Paper]]