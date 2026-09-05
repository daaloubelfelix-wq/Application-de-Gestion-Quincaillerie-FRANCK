"""
Gestion des fournisseurs.
"""

from database import Database


def lister_fournisseurs(terme_recherche=None):
    if terme_recherche:
        return Database.fetch_all(
            "SELECT id, nom, contact, telephone FROM fournisseurs WHERE nom ILIKE %s ORDER BY nom",
            (f"%{terme_recherche}%",),
        )
    return Database.fetch_all("SELECT id, nom, contact, telephone FROM fournisseurs ORDER BY nom")


def articles_fournis(fournisseur_id):
    return Database.fetch_all(
        "SELECT nom, categorie FROM articles WHERE fournisseur_id = %s ORDER BY nom",
        (fournisseur_id,),
    )


def creer_fournisseur(nom, contact, telephone):
    if not nom.strip():
        raise ValueError("Le nom du fournisseur est obligatoire.")
    Database.execute(
        "INSERT INTO fournisseurs (nom, contact, telephone) VALUES (%s, %s, %s)",
        (nom.strip(), contact.strip() or None, telephone.strip() or None),
    )


def modifier_fournisseur(fournisseur_id, nom, contact, telephone):
    if not nom.strip():
        raise ValueError("Le nom du fournisseur est obligatoire.")
    Database.execute(
        "UPDATE fournisseurs SET nom = %s, contact = %s, telephone = %s WHERE id = %s",
        (nom.strip(), contact.strip() or None, telephone.strip() or None, fournisseur_id),
    )
