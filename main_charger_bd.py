import deepface.DeepFace
import pandas as pd
import pathlib
from copy import deepcopy



def charger_df_personne_photo(nom_fichier_txt) -> pd.DataFrame:
    liste_resulats = []

    # extraction des données du fichier
    with open(nom_fichier_txt, 'r') as fichier:
        liste_informations = fichier.readlines()
        for compteur_info in range(len(liste_informations)) :
            liste_informations[compteur_info] = liste_informations[compteur_info].replace('\n', '')

    while len(liste_informations) != 0 :
        liste_temporaire = []
        while not liste_informations == [] and liste_informations[0] != '':
            liste_temporaire.append(liste_informations[0])
            liste_informations.pop(0)

        if len(liste_informations) != 0 and liste_informations[0] == '' :
            liste_informations.pop(0)

        a = ' '.join(liste_temporaire)
        liste_infos_personne = a.split(' ')

        # creation d'un dictionnaire contenant les infos relatives à chaque ligne
        for compteur_liste_infos_personne in range(3, len(liste_infos_personne)):
            dico = {'photo': liste_infos_personne[compteur_liste_infos_personne], 'pseudonyme': liste_infos_personne[0],
                    'prenom': liste_infos_personne[1], 'nom': liste_infos_personne[2]}
            liste_resulats.append(dico)
            compteur_liste_infos_personne += 1

        # 'remise a 0' des listes et compteurs utiles
        liste_infos_personne.clear()
        liste_temporaire.clear()

    df = pd.DataFrame.from_dict(liste_resulats)
    return df



def calculer_representation(chemin: str, dict_photo_id_photo: dict[str, int],
                        model_name: str = 'Facenet', detector_backend: str = 'mtcnn',
                        ) -> pd.DataFrame:
    """

        :param chemin: chemin d'accès au photo (car dans dict_photo_id_photo on n'a que le nom du fichier photo)
        :param dict_photo_id_photo: nom du fichier photo -> id_photo de la bd
        :param model_name:
        :param detector_backend:
        :return: header de la dataframe
                 'nom_fichier', 'id_photo', 'x_boite', 'y_boite', 'largeur_boite', 'hauteur_boite', 'p0000', 'p0001', 'p0002', ...
    """

    liste_dico = []

    liste_photo = [chemin.name for chemin in pathlib.Path(chemin).glob('*.jpg')]


    for chemin in liste_photo :
        chemin = ".\data\\" + chemin
        dico_res = {}
        "print(chemin)"
        embedding = deepface.DeepFace.represent(img_path=chemin, enforce_detection=False, model_name=model_name, detector_backend=detector_backend)
        "print(embedding)"

        # Récupération du nom de l'image
        liste_chemin = chemin.split("\\")
        dico_res['nom_fichier']= liste_chemin[-1]

        # Recuperation de l'id photo à partir du nom du fichier dans le dictionnaire en paramètre
        # Probleme de duplict des clefs si il y a plusieurs visage sur la photo.
        dico_res["id_photo"] = dict_photo_id_photo[dico_res['nom_fichier']]

        # Si la fonction contient plusieurs visages : il faut boucler sur les element de la liste embedding
        for compteur_embedding in range(len(embedding)):
            "print(embedding[compteur_embedding])"

            # Pour ce qui est des information relative à la boite, on les recupère avec deepface et la fonction represent()
            dico_res["x_boite"] = embedding[compteur_embedding]['facial_area']['x']
            dico_res["y_boite"] = embedding[compteur_embedding]['facial_area']['y']
            dico_res["largeur_boite"] = embedding[compteur_embedding]['facial_area']['w']
            dico_res["hauteur_boite"] = embedding[compteur_embedding]['facial_area']['h']


            # Recuperation des information de l'embedding (le vecteur pas la variable)
            for compteur_embedding_vecteur in range(len(embedding[compteur_embedding]['embedding'])) :
                num_vect = '0000'+str(compteur_embedding_vecteur)
                num_vect = num_vect[-4:]
                dico_res[f'p{num_vect}']=embedding[compteur_embedding]['embedding'][compteur_embedding_vecteur]
                "print(embedding[compteur_embedding]['embedding'][compteur_embedding_vecteur])"

            liste_dico.append(dico_res)
            dico_res = deepcopy(dico_res)

    df = pd.DataFrame(liste_dico)

    return df



don = charger_df_personne_photo("identification.txt")
