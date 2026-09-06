"""
Logique métier de la vente.

Circuit réel de la boutique, inspiré de la pharmacie : on ne remet jamais
un document numéroté avant d'avoir reçu l'argent. La comptabilité
enregistre la commande du client (le stock est retiré immédiatement, un
« bon de commande » non fiscal est imprimé, voir
modules/facturation.py::generer_bon_commande_pdf) ; le client va ensuite
payer à la caisse, tenue par le responsable. C'est seulement à
l'encaissement que : la vente compte dans les recettes du jour, ET que le
numéro de facture est attribué et que la facture/le ticket final est
généré (voir encaisser_commande) — jamais avant, pour qu'un numéro de
facture corresponde toujours à un paiement réellement reçu.

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
    Ne crée PAS encore de recette comptable, et n'attribue PAS encore de
    numéro de facture (même si type_document == 'facture') : ça, c'est le
    rôle de encaisser_commande(), au moment où l'argent est réellement
    reçu à la caisse — voir le docstring du module.
    Retourne le dictionnaire de la commande créée.
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

        cur.execute(
            """
            INSERT INTO ventes
                (site_id, utilisateur_id, type_document, statut,
                 sous_total_ht, taux_tva, montant_tva, total_ttc)
            VALUES (%s, %s, %s, 'en_attente', %s, 19.25, %s, %s)
            RETURNING id, date_vente
            """,
            (
                utilisateur["site_id"],
                utilisateur["id"],
                type_document,
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


def encaisser_commande(vente_id, utilisateur_caisse, mode_paiement):
    """
    Encaisse une commande en attente : crée la recette comptable (c'est elle
    qui compte dans les recettes du jour), marque la commande payée, et —
    seulement maintenant, l'argent étant réellement reçu — attribue le
    numéro de facture (si type_document == 'facture') et renvoie tout ce
    qu'il faut pour générer le document final (facture ou ticket) à la
    caisse (voir ui/caisse.py). mode_paiement : voir modules/paiement.py
    (especes, orange_money, mtn_momo, credit_client, autre).
    """
    from modules.paiement import LIBELLES_MODES_PAIEMENT, libelle_mode_paiement

    if mode_paiement not in LIBELLES_MODES_PAIEMENT:
        raise ValueError("Mode de paiement invalide.")

    with Database.transaction() as cur:
        cur.execute(
            """
            SELECT v.site_id, v.total_ttc, v.type_document, v.statut,
                   s.nom AS site_nom, u.nom_complet AS vendeur_nom
            FROM ventes v
            JOIN sites s ON s.id = v.site_id
            JOIN utilisateurs u ON u.id = v.utilisateur_id
            WHERE v.id = %s
            FOR UPDATE OF v
            """,
            (vente_id,),
        )
        vente = cur.fetchone()
        if vente is None or vente["statut"] != "en_attente":
            raise ValueError("Cette commande n'existe pas ou a déjà été traitée.")

        numero_facture = prochain_numero_facture(cur) if vente["type_document"] == "facture" else None

        cur.execute(
            """
            UPDATE ventes
            SET statut = 'payee', utilisateur_caisse_id = %s,
                date_encaissement = NOW(), mode_paiement = %s, numero_facture = %s
            WHERE id = %s
            """,
            (utilisateur_caisse["id"], mode_paiement, numero_facture, vente_id),
        )

        description = f"Encaissement commande client ({libelle_mode_paiement(mode_paiement)})"
        cur.execute(
            """
            INSERT INTO transactions (site_id, utilisateur_id, type, montant, description, vente_id)
            VALUES (%s, %s, 'recette', %s, %s, %s)
            """,
            (vente["site_id"], utilisateur_caisse["id"], vente["total_ttc"], description, vente_id),
        )

        cur.execute(
            """
            SELECT a.nom, l.quantite, l.prix_unitaire
            FROM ventes_lignes l
            JOIN articles a ON a.id = l.article_id
            WHERE l.vente_id = %s
            ORDER BY l.id
            """,
            (vente_id,),
        )
        lignes = cur.fetchall()

    return {
        "id": vente_id,
        "total_ttc": vente["total_ttc"],
        "mode_paiement": mode_paiement,
        "type_document": vente["type_document"],
        "numero_facture": numero_facture,
        "site_nom": vente["site_nom"],
        "vendeur_nom": vente["vendeur_nom"],
        "lignes": lignes,
    }


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
