= Exploration de MV-Adapter pour la génération de textures sur un mesh de canard

== Introduction

La génération de textures à partir de prompt est l'une des potentielles méthodes.

Elle permet de tester rapidement des styles visuels, des couleurs et des formes.

On travaille avec notre propre mesh de canard.

L’objectif est simple : décrire un style et obtenir une texture directement utilisable.

On utilise MV-Adapter pour générer cette texture à partir d’un prompt texte et la texture est ensuite appliqué sur le modèle 3D.

== Pourquoi MV-Adapter

MV-Adapter permet de générer des images cohérentes entre plusieurs vues.

Il s’appuie sur des modèles texte → image pré-entraînés.

Il ajoute une cohérence multi-vues sans modifier le modèle de base.

Il prend aussi en compte la géométrie du canard.

C’est top car on a notre propre mesh de canard.

On veut seulement générer la texture.


== Pipeline

Le pipeline est le suivant :

1. Fournir le mesh de canard 
2. Donner un prompt texte (ex :  superhéros, jeuxvideo, métier )
3. Générer les multi-vues 
4. Reprojeter sur le mesh automatique
5. Générer la texture finale

== Motivation

Une démo text-to-texture existe déjà: #link("https://huggingface.co/spaces/VAST-AI/MV-Adapter-Text2Texture")[#text(fill: blue)[Demo T2T sur hugginsface]]

Donc la méthode est déjà fonctionnelle.

Cela permet :
- de tester rapidement
- de contrôler les prompts
- d’utiliser son propre mesh

C’est adapté pour expérimenter sur le canard.

== Conclusion

MV-Adapter est adapté pour ce type de problème.

C’est une bonne base pour générer des textures sur le canard.

#link("https://arxiv.org/pdf/2412.03632")[#text(fill: blue)[Paper]]