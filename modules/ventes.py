"""
Logique métier de la vente.
Une vente diminue le stock, crée une ligne de transaction comptable
automatiquement, et calcule la TVA à 19,25% (logique centralisée
dans modules/facturation.py pour éviter toute incohérence de taux).
"""

from database import Database
from modules.facturation import calculer_totaux, prochain_numero_facture


def enregistrer_vente(utilisateur, lignes_panier, type_document="ticket"):
    """
    Enregistre une vente complète :
    1. Vérifie le stock disponible pour chaque article
    2. Crée la vente + ses lignes
    3. Diminue le stock et historise le mouvement
    4. Crée la transaction comptable liée (pas de double saisie)
    Retourne le dictionnaire de la vente créée (avec numero_facture si applicable).
    """
    if not lignes_panier:
        raise ValueError("Le panier est vide.")

    # Vérification du stock avant toute écriture
    for ligne in lignes_panier:
        article = Database.fetch_one(
            "SELECT nom, quantite_stock FROM articles WHERE id = %s",
            (ligne["article_id"],),
        )
        if article is None:
            raise ValueError(f"Article introuvable (id {ligne['article_id']}).")
        if article["quantite_stock"] < ligne["quantite"]:
            raise ValueError(
                f"Stock insuffisant pour '{article['nom']}' "
                f"({article['quantite_stock']} disponibles, {ligne['quantite']} demandés)."
            )

    sous_total_ht, montant_tva, total_ttc = calculer_totaux(lignes_panier)

    numero_facture = prochain_numero_facture() if type_document == "facture" else None

    vente = Database.fetch_one(
        """
        INSERT INTO ventes
            (site_id, utilisateur_id, type_document, numero_facture,
             sous_total_ht, taux_tva, montant_tva, total_ttc)
        VALUES (%s, %s, %s, %s, %s, 19.25, %s, %s)
        RETURNING id, numero_facture, date_vente
        """,
        (
            utilisateur["site_id"],
            utilisateur["id"],
            type_document,
            numero_facture,
            sous_total_ht,
            montant_tva,
            total_ttc,
        ),
    )

    for ligne in lignes_panier:
        Database.execute(
            """
            INSERT INTO ventes_lignes (vente_id, article_id, quantite, prix_unitaire)
            VALUES (%s, %s, %s, %s)
            """,
            (vente["id"], ligne["article_id"], ligne["quantite"], ligne["prix_unitaire"]),
        )
        Database.execute(
            "UPDATE articles SET quantite_stock = quantite_stock - %s WHERE id = %s",
            (ligne["quantite"], ligne["article_id"]),
        )
        Database.execute(
            """
            INSERT INTO mouvements_stock (article_id, type, quantite, motif, utilisateur_id)
            VALUES (%s, 'sortie', %s, 'Vente', %s)
            """,
            (ligne["article_id"], ligne["quantite"], utilisateur["id"]),
        )

    Database.execute(
        """
        INSERT INTO transactions (site_id, utilisateur_id, type, montant, description, vente_id)
        VALUES (%s, %s, 'recette', %s, 'Vente au comptant', %s)
        """,
        (utilisateur["site_id"], utilisateur["id"], total_ttc, vente["id"]),
    )

    return {
        "id": vente["id"],
        "numero_facture": vente["numero_facture"],
        "date_vente": vente["date_vente"],
        "sous_total_ht": sous_total_ht,
        "montant_tva": montant_tva,
        "total_ttc": total_ttc,
        "type_document": type_document,
    }


def rechercher_articles(site_id, terme_recherche):
    """Recherche d'articles pour le point de vente, limitée au site de l'utilisateur."""
    return Database.fetch_all(
        """
        SELECT id, nom, prix_vente, quantite_stock
        FROM articles
        WHERE site_id = %s AND nom ILIKE %s
        ORDER BY nom
        LIMIT 20
        """,
        (site_id, f"%{terme_recherche}%"),
    )
