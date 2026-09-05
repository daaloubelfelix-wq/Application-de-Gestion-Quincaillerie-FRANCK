"""
Gestion des comptes utilisateurs — réservé au responsable.
"""

from database import Database
from modules.auth import hacher_mot_de_passe


def lister_utilisateurs():
    return Database.fetch_all(
        """
        SELECT u.id, u.nom_complet, u.identifiant, u.role, u.actif,
               s.nom AS site_nom
        FROM utilisateurs u
        LEFT JOIN sites s ON s.id = u.site_id
        ORDER BY u.nom_complet
        """
    )


def creer_utilisateur(nom_complet, identifiant, mot_de_passe, role, site_id):
    if not nom_complet.strip() or not identifiant.strip():
        raise ValueError("Le nom et l'identifiant sont obligatoires.")
    if len(mot_de_passe) < 4:
        raise ValueError("Le mot de passe doit contenir au moins 4 caractères.")
    if role != "responsable" and site_id is None:
        raise ValueError("Un agent doit être rattaché à un site.")

    existe_deja = Database.fetch_one(
        "SELECT id FROM utilisateurs WHERE identifiant = %s", (identifiant.strip(),)
    )
    if existe_deja:
        raise ValueError(f"L'identifiant '{identifiant}' est déjà utilisé.")

    mot_de_passe_hash = hacher_mot_de_passe(mot_de_passe)
    Database.execute(
        """
        INSERT INTO utilisateurs (nom_complet, identifiant, mot_de_passe_hash, role, site_id, actif)
        VALUES (%s, %s, %s, %s, %s, TRUE)
        """,
        (nom_complet.strip(), identifiant.strip(), mot_de_passe_hash, role,
         None if role == "responsable" else site_id),
    )


def activer_desactiver(utilisateur_id, actif):
    Database.execute("UPDATE utilisateurs SET actif = %s WHERE id = %s", (actif, utilisateur_id))


def reinitialiser_tentatives(utilisateur_id):
    """Déverrouille un compte après trop de tentatives échouées."""
    Database.execute("UPDATE utilisateurs SET tentatives_echouees = 0 WHERE id = %s", (utilisateur_id,))
