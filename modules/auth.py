"""
Authentification des utilisateurs.
Verrouillage du compte après 5 tentatives échouées, comme décidé
lors de la conception.
"""

import bcrypt
from database import Database

MAX_TENTATIVES = 5


def authentifier(identifiant: str, mot_de_passe: str):
    """
    Vérifie l'identifiant et le mot de passe.
    Retourne le dictionnaire utilisateur si succès, ou lève une ValueError
    avec un message clair à afficher à l'écran si échec.
    """
    utilisateur = Database.fetch_one(
        """
        SELECT u.id, u.nom_complet, u.identifiant, u.mot_de_passe_hash,
               u.role, u.site_id, u.actif, u.tentatives_echouees,
               s.nom AS site_nom
        FROM utilisateurs u
        LEFT JOIN sites s ON s.id = u.site_id
        WHERE u.identifiant = %s
        """,
        (identifiant,),
    )

    if utilisateur is None:
        raise ValueError("Identifiant ou mot de passe incorrect.")

    if not utilisateur["actif"]:
        raise ValueError("Ce compte a été désactivé. Contactez le responsable.")

    if utilisateur["tentatives_echouees"] >= MAX_TENTATIVES:
        raise ValueError(
            "Compte verrouillé après plusieurs tentatives échouées. "
            "Contactez le responsable pour le réactiver."
        )

    mot_de_passe_valide = bcrypt.checkpw(
        mot_de_passe.encode("utf-8"),
        utilisateur["mot_de_passe_hash"].encode("utf-8"),
    )

    if not mot_de_passe_valide:
        Database.execute(
            "UPDATE utilisateurs SET tentatives_echouees = tentatives_echouees + 1 WHERE id = %s",
            (utilisateur["id"],),
        )
        raise ValueError("Identifiant ou mot de passe incorrect.")

    # Réinitialise le compteur après une connexion réussie
    Database.execute(
        "UPDATE utilisateurs SET tentatives_echouees = 0 WHERE id = %s",
        (utilisateur["id"],),
    )

    return utilisateur


def hacher_mot_de_passe(mot_de_passe_clair: str) -> str:
    """Utilitaire pour créer un nouveau compte (utilisé par l'écran Utilisateurs)."""
    sel = bcrypt.gensalt()
    return bcrypt.hashpw(mot_de_passe_clair.encode("utf-8"), sel).decode("utf-8")
