"""
Script à lancer quand un utilisateur a oublié son mot de passe.
Redemande un nouveau mot de passe pour un identifiant existant, remet le
compte à zéro (déverrouillé, actif), sans toucher au reste de ses données.

À lancer depuis le dossier du projet, avec le même config.ini que
l'application (pip install -r requirements.txt si besoin).

Usage :
    python reinitialiser_mot_de_passe.py
"""

from database import Database
from modules.auth import hacher_mot_de_passe


def reinitialiser_mot_de_passe():
    identifiant = input("Identifiant du compte à réinitialiser (ex: franck2026) : ").strip()

    utilisateur = Database.fetch_one(
        "SELECT id, nom_complet, actif, tentatives_echouees FROM utilisateurs WHERE identifiant = %s",
        (identifiant,),
    )
    if utilisateur is None:
        print(f"Aucun compte avec l'identifiant '{identifiant}'. Opération annulée.")
        return

    print(f"Compte trouvé : {utilisateur['nom_complet']}"
          f"{' (actuellement désactivé)' if not utilisateur['actif'] else ''}"
          f"{' (actuellement verrouillé après plusieurs échecs)' if utilisateur['tentatives_echouees'] >= 5 else ''}.")

    nouveau_mot_de_passe = input("Nouveau mot de passe : ").strip()
    confirmation = input("Confirmez le nouveau mot de passe : ").strip()

    if nouveau_mot_de_passe != confirmation:
        print("Les deux mots de passe saisis ne correspondent pas. Opération annulée.")
        return
    if not nouveau_mot_de_passe:
        print("Le mot de passe ne peut pas être vide. Opération annulée.")
        return

    mot_de_passe_hash = hacher_mot_de_passe(nouveau_mot_de_passe)

    Database.execute(
        """
        UPDATE utilisateurs
        SET mot_de_passe_hash = %s, tentatives_echouees = 0, actif = TRUE
        WHERE id = %s
        """,
        (mot_de_passe_hash, utilisateur["id"]),
    )

    print(f"\nMot de passe réinitialisé pour '{identifiant}' — le compte est aussi déverrouillé et réactivé.")
    print("Franck peut se reconnecter avec ce nouveau mot de passe.")


if __name__ == "__main__":
    reinitialiser_mot_de_passe()
