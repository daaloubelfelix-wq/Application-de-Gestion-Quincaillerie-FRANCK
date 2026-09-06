"""
Logique métier de la vente.

Circuit réel de la boutique : le client paie d'abord directement à la
caisse, tenue par le responsable, qui note la vente à la main sur le
facturier papier — rien dans l'ordinateur à ce moment. Le responsable (ou
le client) apporte ensuite cette note à la comptabilité, qui saisit tout
dans l'ordinateur EN UNE SEULE FOIS, puisque l'argent est déjà reçu :
c'est cette saisie (enregistrer_vente) qui retire le stock, crée la
recette comptable, attribue le numéro de facture si nécessaire, ET génère
le reçu final à imprimer (voir modules/facturation.py).

Le taux de TVA est calculé une seule fois, dans modules/facturation.py,
pour éviter toute incohérence (actuellement 0% : la marchandise est déjà
taxée à l'achat auprès du fournisseur).
"""

from database import Database
from modules.facturation import calculer_totaux, prochain_numero_facture, TAUX_TVA


def enregistrer_vente(utilisateur, lignes_panier, type_document, mode_paiement):
    """
    Enregistre une vente déjà payée à la caisse, dans une seule transaction
    (tout réussit, ou rien n'est écrit — voir Database.transaction) :
    1. Décrémente le stock de façon atomique (protégé contre la saisie
       simultanée du même article sur deux postes)
    2. Attribue le numéro de facture si type_document == 'facture'
    3. Crée la vente (statut 'payee' directement — l'argent a déjà été
       reçu physiquement) + ses lignes
    4. Crée la recette comptable du jour
    5. Historise le mouvement de stock
    Retourne tout ce qu'il faut pour imprimer le reçu final (voir
    modules/facturation.py::generer_recu_thermique_pdf).
    """
    from modules.paiement import LIBELLES_MODES_PAIEMENT, libelle_mode_paiement

    if not lignes_panier:
        raise ValueError("Le panier est vide.")
    if mode_paiement not in LIBELLES_MODES_PAIEMENT:
        raise ValueError("Mode de paiement invalide.")

    sous_total_ht, montant_tva, total_ttc = calculer_totaux(lignes_panier)

    with Database.transaction() as cur:
        # Décrémente chaque article de façon atomique : la condition
        # quantite_stock >= quantite est vérifiée par PostgreSQL au moment
        # même de l'écriture, donc deux saisies simultanées ne peuvent pas
        # toutes les deux faire passer le stock sous zéro.
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
                 mode_paiement, date_encaissement,
                 sous_total_ht, taux_tva, montant_tva, total_ttc)
            VALUES (%s, %s, %s, %s, 'payee', %s, NOW(), %s, %s, %s, %s)
            RETURNING id, date_vente
            """,
            (
                utilisateur["site_id"],
                utilisateur["id"],
                type_document,
                numero_facture,
                mode_paiement,
                sous_total_ht,
                TAUX_TVA,
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
                VALUES (%s, 'sortie', %s, 'Vente client', %s)
                """,
                (ligne["article_id"], ligne["quantite"], utilisateur["id"]),
            )

        description = f"Vente client ({libelle_mode_paiement(mode_paiement)})"
        cur.execute(
            """
            INSERT INTO transactions (site_id, utilisateur_id, type, montant, description, vente_id)
            VALUES (%s, %s, 'recette', %s, %s, %s)
            """,
            (utilisateur["site_id"], utilisateur["id"], total_ttc, description, vente["id"]),
        )

    return {
        "id": vente["id"],
        "date_vente": vente["date_vente"],
        "sous_total_ht": sous_total_ht,
        "montant_tva": montant_tva,
        "total_ttc": total_ttc,
        "type_document": type_document,
        "numero_facture": numero_facture,
        "mode_paiement": mode_paiement,
        "site_nom": utilisateur["site_nom"],
        "vendeur_nom": utilisateur["nom_complet"],
        "lignes": lignes_panier,
    }


def ventes_du_jour(site_id=None):
    """
    Ventes payées aujourd'hui, affichées à l'écran Historique (responsable)
    pour vérification et, si besoin, annulation d'une saisie erronée.
    """
    condition_site = ""
    params = []
    if site_id is not None:
        condition_site = "AND v.site_id = %s"
        params.append(site_id)

    return Database.fetch_all(
        f"""
        SELECT v.id, v.type_document, v.numero_facture, v.total_ttc, v.mode_paiement,
               v.date_vente, s.nom AS site_nom, u.nom_complet AS enregistree_par
        FROM ventes v
        JOIN sites s ON s.id = v.site_id
        JOIN utilisateurs u ON u.id = v.utilisateur_id
        WHERE v.statut = 'payee' AND v.date_vente::date = CURRENT_DATE {condition_site}
        ORDER BY v.date_vente DESC
        """,
        params,
    )


def annuler_vente(vente_id, utilisateur):
    """
    Annule une vente déjà payée (erreur de saisie) : restitue le stock
    retiré et retire la recette comptable correspondante. Réservé au
    responsable (voir ui/caisse.py) — l'argent a déjà été physiquement
    reçu, seul celui qui l'a en main sait si une correction est légitime.
    """
    with Database.transaction() as cur:
        cur.execute(
            "SELECT statut FROM ventes WHERE id = %s FOR UPDATE",
            (vente_id,),
        )
        vente = cur.fetchone()
        if vente is None:
            raise ValueError("Cette vente n'existe pas.")
        if vente["statut"] != "payee":
            raise ValueError("Seule une vente payée peut être annulée depuis cet écran.")

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
                VALUES (%s, 'entree', %s, 'Annulation vente', %s)
                """,
                (ligne["article_id"], ligne["quantite"], utilisateur["id"]),
            )

        cur.execute("DELETE FROM transactions WHERE vente_id = %s", (vente_id,))
        cur.execute("UPDATE ventes SET statut = 'annulee' WHERE id = %s", (vente_id,))


def rechercher_articles(site_id, terme_recherche):
    """Recherche d'articles pour l'enregistrement d'une vente, limitée au site de l'utilisateur."""
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
