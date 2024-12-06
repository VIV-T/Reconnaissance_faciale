## Import ##
import pathlib
import mysql.connector
from mysql.connector import errorcode
import pandas as pd
from copy import deepcopy
from main_charger_bd import charger_df_personne_photo, calculer_representation

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from scipy.spatial.distance import cosine


def creer_connexion():
    try:
        connexion = mysql.connector.connect(
            host="devbdd.iutmetz.univ-lorraine.fr",
            user="e1735u_appli",
            password="32313706",
            database="e1735u_Projet_visage"
        )
    except mysql.connector.Error as err:

        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Erreur: login ou mot de passe incorrect")
            return None
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Erreur: la base de données n'existe pas")
            return None
        else:
            print(err)
            return None

    return connexion


####

# Permet de vider la BD
def vider_bd() -> None:
    connexion = creer_connexion()

    if connexion is None:
        return None

    try:
        curseur = connexion.cursor()

        sql1 = 'DELETE  FROM Apparaitre WHERE id_personne <> 0 AND id_photo <> 0;'
        sql2 = 'DELETE  FROM Personne WHERE id_personne <> 0;'
        sql3 = 'DELETE FROM Photo WHERE id_photo <> 0; '
        curseur.execute(sql1)
        curseur.execute(sql2)
        curseur.execute(sql3)

        resultat = None
        connexion.commit()
        curseur.close()

    except:
        print("Erreur: requête non exécutée")
        resultat = None

    connexion.close()

    return resultat


## Fonctions d'insertion :
# Insertion des informations d'une personne
def inserer_personne(df_personne: pd.DataFrame) -> dict[str, int]:
    connexion = creer_connexion()

    if connexion is None:
        return None


    try:
        curseur = connexion.cursor()

        # Boucler sur le dataframe afin d'inserer toutes les lignes du dataframe
        for personne in df_personne.itertuples():
            sql_insert = "INSERT INTO Personne (pseudonyme, Prénom, Nom) VALUES (%s, %s, %s);"

            # indicage à 2 car il y a 5 composante au tuple et les 2 premieres sont l'index et
            # le nom de l'image trombi.
            try :
                curseur.execute(sql_insert, personne[2:])
            except mysql.connector.errors.IntegrityError :
                continue

        sql_get_id = "SELECT * FROM Personne"
        curseur.execute(sql_get_id)
        res = curseur.fetchall()
        identifiant = {}

        for compteur_df in range(len(df_personne['photo'])):
            for compteur_res in range(len(res)):
                if res[compteur_res][1] == df_personne['pseudonyme'][compteur_df]:
                    identifiant[df_personne['photo'][compteur_df]] = res[compteur_res][0]

        connexion.commit()
        curseur.close()


    except:
        print("Erreur: requête inserer_personne non exécutée")
        identifiant = None

    connexion.close()
    return identifiant


# Insertion des informations d'une photo
def inserer_photo(liste_photo: list[str]) -> dict[str, int]:
    connexion = creer_connexion()

    if connexion is None:
        return None

    try:
        curseur = connexion.cursor()

        for photo in liste_photo:
            sql_insert = "INSERT INTO Photo (nom_fichier) VALUES (%s);"

            curseur.execute(sql_insert, [photo])

        connexion.commit()

        try:
            sql_get_id = "SELECT * FROM Photo;"
            curseur.execute(sql_get_id)
            res = curseur.fetchall()
            identifiant = {}

            for compteur_res in range(len(res)):
                identifiant[res[compteur_res][1]] = res[compteur_res][0]

        except:
            print("Impossible de créer le dictionnaire")
            identifiant = None

        connexion.close()

    except:
        print("Erreur: requête inserer_photo non exécutée")
        identifiant = None

        connexion.close()

    return identifiant


# Recuperation des informations de la table Photo
def get_dict_photo():
    connexion = creer_connexion()

    if connexion is None:
        return None

    try:
        curseur = connexion.cursor()
        sql_get_id = "SELECT * FROM Photo;"
        curseur.execute(sql_get_id)
        res = curseur.fetchall()
        identifiant = {}

        for compteur_res in range(len(res)):
            identifiant[res[compteur_res][1]] = res[compteur_res][0]

    except:
        print("Impossible de créer le dictionnaire")
        identifiant = None

    connexion.close()
    return identifiant


# Fonction d'insertion dans la table Apparaitre
def inserer_apparition(dict_photo_id_personne: dict[str, int], df_representations: pd.DataFrame,
                       seuil_distance: float = 0.5) -> None:

    ## Première partie : construction du dataframe pour l'insertion dans la BD

    # On cherche les correspondances entre le df_representation et le dict_photo.
    # on créer un df de résultats qui va etre modifié petit à petit pour éviter de toucher au df d'input
    df_insertion = deepcopy(df_representations)
    df_insertion = df_insertion.rename(columns={'nom_fichier':'id_personne'})


    for representation in df_representations.iterrows() :
        vecteurs_representation = df_representations.iloc[representation[0],8:]

        # On boucle sur le dictionnaire des photo du trombi
        for photo in dict_photo_id_personne.keys() :

            # on boucle sur le df_representation
            seuil_distance_bis = seuil_distance
            for representation_photo in df_representations.iterrows() :
                # ON verifie si le nom de fichier dans le dictionnaire correspond au nom du fichier dans le df
                if representation_photo[1]['nom_fichier'] == photo :
                    # Si correspondance, enregistrement des vecteurs de représentation.
                    vecteurs_representation_photo = df_representations.iloc[representation_photo[0],8:]

                    vecteurs_representation_numpy = vecteurs_representation.to_numpy()
                    vecteurs_representation_photo_numpy = vecteurs_representation_photo.to_numpy()

                    # Calcul de la distance entre les deux vecteurs
                    distance = cosine(vecteurs_representation_numpy, vecteurs_representation_photo_numpy)


                    # Comparaison de la distance calculée à la distance seuil
                    # ou à la distance min calculée précédement
                    if distance <= seuil_distance_bis :
                        df_insertion.loc[representation[0],'id_personne']=dict_photo_id_personne[photo]
                        seuil_distance_bis = distance


    # Suppression des colonnes contenant l'embbedding
    df_insertion = df_insertion.iloc[:, :8]

    # Suppression des lignes où il n'y a pas de correspondances.
    for index_insertion,ligne_df_insertion in df_insertion.iterrows() :
        try :
            ligne_df_insertion['id_personne'] = int(ligne_df_insertion['id_personne'])
            infos_apparition = []

            infos_apparition.append(df_insertion.iloc[index_insertion, 0])
            infos_apparition.append(int(df_insertion.iloc[index_insertion, 1]))
            infos_apparition.append(int(df_insertion.iloc[index_insertion, 2]))
            infos_apparition.append(int(df_insertion.iloc[index_insertion, 3]))
            infos_apparition.append(int(df_insertion.iloc[index_insertion, 4]))
            infos_apparition.append(int(df_insertion.iloc[index_insertion, 5]))
            infos_apparition.append(float(df_insertion.iloc[index_insertion, 6]))
            infos_apparition.append(float(df_insertion.iloc[index_insertion, 7]))


            connexion = creer_connexion()

            if connexion is None:
                return None
            else:
                try:
                    curseur = connexion.cursor()


                    sql_insert = '''INSERT IGNORE INTO Apparaitre (id_personne, id_photo, x_boite, y_boite, largeur_boite, hauteur_boite, x_projection, y_projection) 
                                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s
                                          ) ;'''

                    curseur.execute(sql_insert, infos_apparition)

                    connexion.commit()
                    curseur.close()

                except:
                    print('Erreur: requête non exécutée')
                    identifiant = None

                connexion.close()


        except :
            df_insertion.drop(index_insertion, inplace=True)

    return df_insertion


# Réalisation de l'ACP + ajout des projection sur les 2 axes au dataframe.
def ajouter_projection(representation):
    coord_x = []
    coord_y = []

    df = representation
    # code ACP (sur le df representation)
    scaler = StandardScaler().fit(representation.iloc[:, 6:])
    data_centre_reduit = scaler.transform(representation.iloc[:, 6:])

    acp = PCA(n_components=2)
    acp.fit(data_centre_reduit)
    composante_principale = acp.transform(data_centre_reduit)


    for elem in composante_principale :
        coord_x.append(elem[0])
        coord_y.append(elem[1])

    df.insert(6, 'x_projection', coord_x, allow_duplicates=False)
    df.insert(7, 'y_projection', coord_y, allow_duplicates=False)

    return df


####    Execution   ####

# Appel de toutes les methodes precedentes
def main_charger_bd():

    don = charger_df_personne_photo("identification.txt")

    path_file_photo = ".\\data\\"
    liste_photo = [path_file_photo.name for path_file_photo in pathlib.Path(path_file_photo).glob('*.jpg')]


    # on vide la base de données
    vider_bd()

    # remplissage de la base de données : dans les tables personne et photo
    # + construction des dictionnaires utiles pour la suite
    dict_photo_id_personne = inserer_personne(don)
    dico_photo = inserer_photo(liste_photo)

    #print(path_file_photo)
    #print(dico_photo)
    print(liste_photo)

    # application des fonction de calcul d'embedding + ACP pour préparer l'insertion dans la table apparaitre.
    df_representation = calculer_representation(path_file_photo, dico_photo)
    #print(df_representation)
    df_representation = ajouter_projection(df_representation)

    # Insertion dans la BD : table apparaitre
    inserer_apparition(dict_photo_id_personne, df_representation)


# Utile pour le module 'main_ihm.py'
def obtenir_df_projection() -> pd.DataFrame:
    connexion = creer_connexion()
    dico_res = {'pseudonyme':[], 'x_projection':[], 'y_projection':[]}

    if connexion is None:
        return None

    try :
        curseur = connexion.cursor()
        sql_get_proj = "SELECT id_personne, x_projection, y_projection FROM Apparaitre;"
        curseur.execute(sql_get_proj)
        proj = curseur.fetchall()

        sql_get_pseudo = "SELECT id_personne, pseudonyme from Personne"
        curseur.execute(sql_get_pseudo)
        pseudo = curseur.fetchall()

    except:
        print('requette non executée')
        return None

    # parcours des boucles obtenues avec les requettes pour créer le dictionnaire qui permet de créer le dataframe.
    for compteur_list_proj in range(len(proj)):
        for compteur_list_pseudo in range(len(pseudo)):
            if proj[compteur_list_proj][0] == pseudo[compteur_list_pseudo][0]:
                dico_res["pseudonyme"].append(pseudo[compteur_list_pseudo][1])
                dico_res["x_projection"].append(proj[compteur_list_proj][1])
                dico_res["y_projection"].append(proj[compteur_list_proj][2])

    df = pd.DataFrame.from_dict(dico_res)

    return df

# Utile pour le module 'main_ihm.py'
def obtenir_df_coapparition(id_personne = 0)-> pd.DataFrame:
    connexion = creer_connexion()
    dico_res = {'pseudonyme1':[], 'pseudonyme2':[], 'nb_apparition':[]}

    if connexion is None:
        return None

    try :
        curseur = connexion.cursor()

        # cas general
        if id_personne == 0 :
            sql_get_co_app = """
                            Select id_1, id_2, count(*)
                            From (
                                    Select Apparaitre1.id_personne as id_1,  Apparaitre2.id_personne as id_2, Apparaitre2.id_photo
                                    From Apparaitre as Apparaitre1 Join Apparaitre as Apparaitre2 using (id_photo)
                                    Where Apparaitre1.id_photo = Apparaitre2.id_photo and Apparaitre1.id_personne <> Apparaitre2.id_personne  and Apparaitre1.id_personne < Apparaitre2.id_personne
                            ) as Coapparition
                            Group By id_1, id_2
                            ;"""

        # cas particulier
        else :
            sql_get_co_app = f"""
                            Select *
                            From(
                                Select id_1, id_2, count(*)
                                From (
                                        Select Apparaitre1.id_personne as id_1,  Apparaitre2.id_personne as id_2, Apparaitre2.id_photo
                                        From Apparaitre as Apparaitre1 Join Apparaitre as Apparaitre2 using (id_photo)
                                        Where Apparaitre1.id_photo = Apparaitre2.id_photo and Apparaitre1.id_personne <> Apparaitre2.id_personne  and Apparaitre1.id_personne < Apparaitre2.id_personne
                                ) as Coapparition
                                Group By id_1, id_2
                            ) as CompteCoapparition
                            Where id_1 = {id_personne} or id_2 = {id_personne}
                            ;"""


        curseur.execute(sql_get_co_app)
        co_app = curseur.fetchall()


        sql_get_pseudo = "SELECT id_personne, pseudonyme from Personne"
        curseur.execute(sql_get_pseudo)
        pseudo = curseur.fetchall()

    except:
        print('Requette non executée')
        return None

    # parcours des boucles obtenues avec les requettes pour créer le dictionnaire qui permet de créer le dataframe.
    for compteur_list_co_app in range(len(co_app)):
        for compteur_list_pseudo in range(len(pseudo)):
            if co_app[compteur_list_co_app][0]==pseudo[compteur_list_pseudo][0]:
                dico_res['pseudonyme1'].append(pseudo[compteur_list_pseudo][1])
            elif co_app[compteur_list_co_app][1]==pseudo[compteur_list_pseudo][0]:
                dico_res['pseudonyme2'].append(pseudo[compteur_list_pseudo][1])
        dico_res['nb_apparition'].append(co_app[compteur_list_co_app][2])


    df = pd.DataFrame.from_dict(dico_res)

    return df

# Utile pour le module 'main_ihm.py'
def obtenir_dict_pers ():
    connexion = creer_connexion()
    dico_res = {}

    if connexion is None:
        return None

    try :
        curseur = connexion.cursor()
        sql_get_pers = """
                        Select pseudonyme, id_personne
                        From Personne
                        ;"""

        curseur.execute(sql_get_pers)
        liste_pers = curseur.fetchall()


    except:
        print('Requette non executée')
        return None


    for compteur in range(len(liste_pers)) :
        dico_res[liste_pers[compteur][0]] = liste_pers[compteur][1]

    return dico_res



### Execution ###

# condition : si le prog est executé en tant que code principal, on initialise la bd
if __name__=='__main__' :
    main_charger_bd()