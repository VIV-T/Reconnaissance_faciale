# Reconnaissance_faciale

## Introduction

Ce projet à été réalisé dans un contexte universitaire (2e année de BUT).
Le but était de manipuler une grande diversité de bibliothèque Python en matière de manipulation de données (Pandas, Sklearn) et de nous introduire à la manipulation d'outils d'intelligence artificielle notamment en terme de reconnaissance faciale (bibliothèque Python : DeepFace).

Nous avons pu aussi développer une interface homme machine (IHM) simple contenant les résultats d'une Analyse en Composante Principale (ACP) et un graphe de distance de co-apparition des personnes identifiée sur les photos.

Nous avons basé notre application sur des photos issues de la franchise Star Wars.


## Explication de l'arborescence des fichiers

Dans le dossier "./data", vous trouverez toutes les photos utilisées lors du projet.
Le scripts SQL de création de table nous permet de créer les tables SQL dans la base données.
Dans le script Python "main_charger_bd" se trouve le code Python relatif à la connexion à la base de données et tout les utilitaire relatifs à l'insertion des données en base et au calcul sur les données. La base données ici utilisée est une base de données universitaire.
Le script "bd" permet d'appliquer les utilitaires du scripts précédents sur nos photos et de réaliser l'ACP (entre autre).
Enfin le script "main_ihm" permet de gérer l'IHM développée sur Tkinter.

Des captures d'écran de la base de donnéesq et une vidéo de l'application sont aussi disponibles dans le repository.
