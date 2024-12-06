CREATE TABLE Personne(
   id_personne INT AUTO_INCREMENT,
   pseudonyme VARCHAR(15) UNIQUE NOT NULL,
   Nom VARCHAR(20) NOT NULL,
   Prénom VARCHAR(20) NOT NULL,
   PRIMARY KEY(id_Personne)
);

CREATE TABLE Photo(
   id_photo INT AUTO_INCREMENT,
   nom_fichier VARCHAR(50) NOT NULL,
   PRIMARY KEY(id_photo),
   UNIQUE(nom_fichier)
);
CREATE TABLE Apparaitre(
   id_personne INT AUTO_INCREMENT,
   id_photo INT,
   x_boite DOUBLE NOT NULL,
   y_boite DOUBLE NOT NULL,
   largeur_boite DOUBLE NOT NULL,
   hauteur_boite DOUBLE NOT NULL,
   x_projection DECIMAL(15,2) NOT NULL,
   y_projection DECIMAL(15,2) NOT NULL,
   PRIMARY KEY(id_Personne, id_photo),
   FOREIGN KEY(id_Personne) REFERENCES Personne(id_Personne),
   FOREIGN KEY(id_photo) REFERENCES Photo(id_photo)
);

                     