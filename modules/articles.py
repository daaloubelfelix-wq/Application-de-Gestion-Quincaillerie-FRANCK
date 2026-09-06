"""
Gestion des articles : création, modification, et ajustement manuel de stock.
Toutes les opérations sont automatiquement limitées au site de l'utilisateur
connecté (un agent ne peut jamais créer un article sur l'autre site).
"""

from database import Database


def lister_articles(site_id=None, terme_recherche=None):
    """site_id=None (responsable uniquement) consolide tous les sites."""
    conditions = []
    params = []

    if site_id is not None:
        conditions.append("a.site_id = %s")
        params.append(site_id)

    if terme_recherche:
        conditions.append("a.nom ILIKE %s")
        params.append(f"%{terme_recherche}%")

    clause_where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    requete = f"""
        SELECT a.id, a.nom, a.categorie, a.unite, a.prix_achat, a.prix_vente,
               a.quantite_stock, a.seuil_alerte, a.fournisseur_id, a.site_id, s.nom AS site_nom
        FROM articles a
        JOIN sites s ON s.id = a.site_id
        {clause_where}
        ORDER BY a.nom
    """
    return Database.fetch_all(requete, params)


def creer_article(site_id, nom, categorie, unite, prix_achat, prix_vente,
                   quantite_initiale, seuil_alerte, fournisseur_id=None):
    """
    prix_vente peut valoir 0 : cas de l'agent stock, qui crée l'article
    sans en fixer le prix (réservé au responsable) — tant qu'il vaut 0,
    l'article n'apparaît pas dans la recherche de vente, voir
    modules/ventes.py::rechercher_articles.
    """
    if not nom.strip():
        raise ValueError("Le nom de l'article est obligatoire.")
    if prix_vente < 0:
        raise ValueError("Le prix de vente ne peut pas être négatif.")
    if quantite_initiale < 0:
        raise ValueError("La quantité ne peut pas être négative.")

    article = Database.fetch_one(
        """
        INSERT INTO articles
            (nom, categorie, unite, prix_achat, prix_vente,
             quantite_stock, seuil_alerte, site_id, fournisseur_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (nom.strip(), categorie, unite, prix_achat, prix_vente,
         quantite_initiale, seuil_alerte, site_id, fournisseur_id),
    )
    return article["id"]


def modifier_article(article_id, nom, categorie, unite, prix_achat, prix_vente,
                      seuil_alerte, utilisateur_id, fournisseur_id=None):
    """
    Toute modification de prix_achat/prix_vente est enregistrée dans
    historique_prix_articles (qui, quand, ancien montant, nouveau montant) —
    sans cette traçabilité, un prix modifié en douce ouvre la porte au vol.
    Le formulaire (ui/formulaire_article.py) réserve déjà ces deux champs
    au responsable pour un article existant ; ceci est la seconde ligne de
    défense, côté logique métier.
    """
    if not nom.strip():
        raise ValueError("Le nom de l'article est obligatoire.")
    if prix_vente < 0:
        raise ValueError("Le prix de vente ne peut pas être négatif.")

    with Database.transaction() as cur:
        cur.execute("SELECT prix_achat, prix_vente FROM articles WHERE id = %s FOR UPDATE", (article_id,))
        article_actuel = cur.fetchone()
        if article_actuel is None:
            raise ValueError("Article introuvable.")

        cur.execute(
            """
            UPDATE articles
            SET nom = %s, categorie = %s, unite = %s,
                prix_achat = %s, prix_vente = %s, seuil_alerte = %s, fournisseur_id = %s
            WHERE id = %s
            """,
            (nom.strip(), categorie, unite, prix_achat, prix_vente, seuil_alerte, fournisseur_id, article_id),
        )

        prix_ont_change = (
            float(article_actuel["prix_achat"]) != float(prix_achat)
            or float(article_actuel["prix_vente"]) != float(prix_vente)
        )
        if prix_ont_change:
            cur.execute(
                """
                INSERT INTO historique_prix_articles
                    (article_id, utilisateur_id, ancien_prix_achat, nouveau_prix_achat,
                     ancien_prix_vente, nouveau_prix_vente)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (article_id, utilisateur_id, article_actuel["prix_achat"], prix_achat,
                 article_actuel["prix_vente"], prix_vente),
            )


def derniere_modification_prix(article_id):
    """Dernier changement de prix enregistré pour cet article, ou None."""
    return Database.fetch_one(
        """
        SELECT h.ancien_prix_achat, h.nouveau_prix_achat, h.ancien_prix_vente,
               h.nouveau_prix_vente, h.date_modification, u.nom_complet
        FROM historique_prix_articles h
        JOIN utilisateurs u ON u.id = h.utilisateur_id
        WHERE h.article_id = %s
        ORDER BY h.date_modification DESC
        LIMIT 1
        """,
        (article_id,),
    )


def ajuster_stock_manuellement(article_id, type_mouvement, quantite, motif, utilisateur_id):
    """
    type_mouvement : 'entree' ou 'sortie'
    Utilisé par exemple lors d'une réception fournisseur (entrée)
    ou d'une casse/perte constatée (sortie).
    """
    if type_mouvement not in ("entree", "sortie"):
        raise ValueError("Type de mouvement invalide.")
    if quantite <= 0:
        raise ValueError("La quantité doit être supérieure à 0.")

    variation = quantite if type_mouvement == "entree" else -quantite

    with Database.transaction() as cur:
        # Condition vérifiée par PostgreSQL au moment de l'écriture : protège
        # contre une sortie simultanée depuis un autre poste (voir modules/ventes.py).
        cur.execute(
            """
            UPDATE articles
            SET quantite_stock = quantite_stock + %s
            WHERE id = %s AND quantite_stock + %s >= 0
            RETURNING nom
            """,
            (variation, article_id, variation),
        )
        resultat = cur.fetchone()
        if resultat is None:
            cur.execute("SELECT nom, quantite_stock FROM articles WHERE id = %s", (article_id,))
            article = cur.fetchone()
            if article is None:
                raise ValueError("Article introuvable.")
            raise ValueError(
                f"Stock insuffisant pour '{article['nom']}' ({article['quantite_stock']} disponibles)."
            )

        cur.execute(
            """
            INSERT INTO mouvements_stock (article_id, type, quantite, motif, utilisateur_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (article_id, type_mouvement, quantite, motif, utilisateur_id),
        )


def articles_en_alerte(site_id=None):
    """
    Articles dont le stock est descendu au seuil d'alerte ou en dessous.
    site_id=None consolide les deux sites (utilisé par le tableau de bord
    mobile du responsable).
    """
    condition_site = ""
    params = []
    if site_id is not None:
        condition_site = "AND a.site_id = %s"
        params.append(site_id)

    return Database.fetch_all(
        f"""
        SELECT a.id, a.nom, a.quantite_stock, a.seuil_alerte, s.nom AS site_nom
        FROM articles a
        JOIN sites s ON s.id = a.site_id
        WHERE a.quantite_stock <= a.seuil_alerte {condition_site}
        ORDER BY a.quantite_stock ASC
        """,
        params,
    )
