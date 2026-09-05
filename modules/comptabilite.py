"""
Gestion de la comptabilité.
Les ventes créent déjà automatiquement une ligne "recette" (voir modules/ventes.py).
Ce module gère la saisie manuelle des dépenses et des recettes hors-vente,
ainsi que la consultation de l'historique et des totaux du jour.
"""

from datetime import date
from database import Database


def saisir_transaction(utilisateur, type_transaction, montant, description):
    if type_transaction not in ("recette", "depense"):
        raise ValueError("Type de transaction invalide.")
    if montant <= 0:
        raise ValueError("Le montant doit être supérieur à 0.")
    if not description.strip():
        raise ValueError("Une description est requise.")

    Database.execute(
        """
        INSERT INTO transactions (site_id, utilisateur_id, type, montant, description)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (utilisateur["site_id"], utilisateur["id"], type_transaction, montant, description.strip()),
    )


def totaux_du_jour(site_id=None):
    """site_id=None agrège les deux sites (utilisé par le tableau de bord mobile du responsable)."""
    aujourd_hui = date.today()

    condition_site = ""
    params = [aujourd_hui]
    if site_id is not None:
        condition_site = "AND site_id = %s"
        params.append(site_id)

    recettes = Database.fetch_one(
        f"""
        SELECT COALESCE(SUM(montant), 0) AS total FROM transactions
        WHERE type = 'recette' AND date_transaction::date = %s {condition_site}
        """,
        params,
    )
    depenses = Database.fetch_one(
        f"""
        SELECT COALESCE(SUM(montant), 0) AS total FROM transactions
        WHERE type = 'depense' AND date_transaction::date = %s {condition_site}
        """,
        params,
    )

    return {
        "recettes": float(recettes["total"]),
        "depenses": float(depenses["total"]),
        "solde_net": float(recettes["total"]) - float(depenses["total"]),
    }


def historique_transactions(site_id, limite=30):
    return Database.fetch_all(
        """
        SELECT t.id, t.type, t.montant, t.description, t.date_transaction,
               u.nom_complet AS auteur
        FROM transactions t
        JOIN utilisateurs u ON u.id = t.utilisateur_id
        WHERE t.site_id = %s
        ORDER BY t.date_transaction DESC
        LIMIT %s
        """,
        (site_id, limite),
    )
