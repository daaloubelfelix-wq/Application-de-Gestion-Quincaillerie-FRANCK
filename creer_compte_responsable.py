"""
Script à exécuter UNE SEULE FOIS pour créer le premier compte responsable.
À lancer depuis le dossier du projet, après avoir créé les tables
avec creation_base_donnees.sql et installé les dépendances
(pip install -r requirements.txt).

Usage :
    python creer_compte_responsable.py
"""

from database import Database
from modules.auth import hacher_mot_de_passe


def creer_compte_responsable():
    nom_complet = input("Nom complet du responsable : ").strip()
    identifiant = input("Identifiant de connexion (ex: f.franck) : ").strip()
    mot_de_passe = input("Mot de passe initial : ").strip()

    existe_deja = Database.fetch_one(
        "SELECT id FROM utilisateurs WHERE identifiant = %s", (identifiant,)
    )
    if existe_deja:
        print(f"Un compte avec l'identifiant '{identifiant}' existe déjà. Opération annulée.")
        return

    mot_de_passe_hash = hacher_mot_de_passe(mot_de_passe)

    Database.execute(
        """
        INSERT INTO utilisateurs (nom_complet, identifiant, mot_de_passe_hash, role, site_id, actif)
        VALUES (%s, %s, %s, 'responsable', NULL, TRUE)
        """,
        (nom_complet, identifiant, mot_de_passe_hash),
    )

    print(f"\nCompte responsable créé avec succès pour '{identifiant}'.")
    print("Vous pouvez maintenant lancer l'application avec : python main.py")


if __name__ == "__main__":
    creer_compte_responsable()
