"""
Logique métier de la vente.

Circuit réel de la boutique : la comptabilité enregistre la commande du
client (le stock est retiré immédiatement, un ticket "montant à payer" est
imprimé) ; le client va ensuite payer à la caisse, tenue par le responsable.
C'est seulement à l'encaissement que la vente compte dans les recettes du
jour — pas de double comptage, pas de recette avant que l'argent soit
réellement reçu.

Le taux de TVA (19,25%) est calculé une seule fois, dans
modules/facturation.py, pour éviter toute incohérence.
"""

from database import Database
from modules.facturation import calculer_totaux, prochain_numero_facture


def enregistrer_commande(utilisateur, lignes_panier, type_document="ticket"):
    """
    Enregistre la commande d'un client, dans une seule transaction (tout
    réussit, ou rien n'est écrit — voir Database.transaction) :
    1. Décrémente le stock de façon atomique (protégé contre la commande
       simultanée du même article sur deux postes)
    2. Crée la vente (statut 'en_attente') + ses lignes
    3. Historise chaque mouvement de stock
    Ne crée PAS encore de recette comptable : ça, c'est le rôle de
    encaisser_commande(), au moment où l'argent est réellement reçu à la
    caisse.
    Retourne le dictionnaire de la commande créée (avec numero_facture si
    applicable).
    """
    if not lignes_panier:
        raise ValueError("Le panier est vide.")

    sous_total_ht, montant_tva, total_ttc = calculer_totaux(lignes_panier)

    with Database.transaction() as cur:
        # Décrémente chaque article de façon atomique : la condition
        # quantite_stock >= quantite est vérifiée par PostgreSQL au moment
        # même de l'écriture, donc deux commandes simultanées ne peuvent
        # pas toutes les deux faire passer le stock sous zéro.
        for ligne in lignes_panier:
            cur.execute(
                """
                UPDATE articles
                SET quantite_stock = quantite_stock - %s
                WHERE id = %s AND quantite_stock >= %s
                RETURNING nom
                """,
                (ligne["quantite"], ligne["article_id"], ligne["quantite"]),
            )
            resultat = cur.fetchone()
            if resultat is None:
                cur.execute("SELECT nom, quantite_stock FROM articles WHERE id = %s", (ligne["article_id"],))
                article = cur.fetchone()
                if article is None:
                    raise ValueError(f"Article introuvable (id {ligne['article_id']}).")
                raise ValueError(
                    f"Stock insuffisant pour '{article['nom']}' "
                    f"({article['quantite_stock']} disponibles, {ligne['quantite']} demandés)."
                )

        numero_facture = prochain_numero_facture(cur) if type_document == "facture" else None

        cur.execute(
            """
            INSERT INTO ventes
                (site_id, utilisateur_id, type_document, numero_facture, statut,
                 sous_total_ht, taux_tva, montant_tva, total_ttc)
            VALUES (%s, %s, %s, %s, 'en_attente', %s, 19.25, %s, %s)
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
        vente = cur.fetchone()

        for ligne in lignes_panier:
            cur.execute(
                """
                INSERT INTO ventes_lignes (vente_id, article_id, quantite, prix_unitaire)
                VALUES (%s, %s, %s, %s)
                """,
                (vente["id"], ligne["article_id"], ligne["quantite"], ligne["prix_unitaire"]),
            )
            cur.execute(
                """
                INSERT INTO mouvements_stock (article_id, type, quantite, motif, utilisateur_id)
                VALUES (%s, 'sortie', %s, 'Commande client', %s)
                """,
                (ligne["article_id"], ligne["quantite"], utilisateur["id"]),
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


def commandes_en_attente(site_id=None):
    """Commandes enregistrées mais pas encore payées, affichées à la caisse."""
    condition_site = ""
    params = []
    if site_id is not None:
        condition_site = "AND v.site_id = %s"
        params.append(site_id)

    return Database.fetch_all(
        f"""
        SELECT v.id, v.type_document, v.numero_facture, v.total_ttc, v.date_vente,
               s.nom AS site_nom, u.nom_complet AS enregistree_par
        FROM ventes v
        JOIN sites s ON s.id = v.site_id
        JOIN utilisateurs u ON u.id = v.utilisateur_id
        WHERE v.statut = 'en_attente' {condition_site}
        ORDER BY v.date_vente ASC
        """,
        params,
    )


def encaisser_commande(vente_id, utilisateur_caisse):
    """
    Encaisse une commande en attente : crée la recette comptable (c'est elle
    qui compte dans les recettes du jour) et marque la commande payée.
    """
    with Database.transaction() as cur:
        cur.execute(
            """
            UPDATE ventes
            SET statut = 'payee', utilisateur_caisse_id = %s, date_encaissement = NOW()
            WHERE id = %s AND statut = 'en_attente'
            RETURNING site_id, total_ttc
            """,
            (utilisateur_caisse["id"], vente_id),
        )
        vente = cur.fetchone()
        if vente is None:
            raise ValueError("Cette commande n'existe pas ou a déjà été traitée.")

        cur.execute(
            """
            INSERT INTO transactions (site_id, utilisateur_id, type, montant, description, vente_id)
            VALUES (%s, %s, 'recette', %s, 'Encaissement commande client', %s)
            """,
            (vente["site_id"], utilisateur_caisse["id"], vente["total_ttc"], vente_id),
        )

    return {"id": vente_id, "total_ttc": vente["total_ttc"]}


def annuler_commande(vente_id, utilisateur):
    """
    Annule une commande en attente (client reparti sans payer) et restitue
    le stock retiré au moment de la commande.
    """
    with Database.transaction() as cur:
        cur.execute(
            "SELECT statut FROM ventes WHERE id = %s",
            (vente_id,),
        )
        vente = cur.fetchone()
        if vente is None:
            raise ValueError("Cette commande n'existe pas.")
        if vente["statut"] != "en_attente":
            raise ValueError("Seule une commande en attente de paiement peut être annulée.")

        cur.execute(
            "SELECT article_id, quantite FROM ventes_lignes WHERE vente_id = %s",
            (vente_id,),
        )
        lignes = cur.fetchall()

        for ligne in lignes:
            cur.execute(
                "UPDATE articles SET quantite_stock = quantite_stock + %s WHERE id = %s",
                (ligne["quantite"], ligne["article_id"]),
            )
            cur.execute(
                """
                INSERT INTO mouvements_stock (article_id, type, quantite, motif, utilisateur_id)
                VALUES (%s, 'entree', %s, 'Annulation commande', %s)
                """,
                (ligne["article_id"], ligne["quantite"], utilisateur["id"]),
            )

        cur.execute(
            "UPDATE ventes SET statut = 'annulee' WHERE id = %s",
            (vente_id,),
        )


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
