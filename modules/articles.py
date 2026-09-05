"""
Gestion des articles : création, modification, et ajustement manuel de stock.
Toutes les opérations sont automatiquement limitées au site de l'utilisateur
connecté (un agent ne peut jamais créer un article sur l'autre site).
"""

from database import Database


def lister_articles(site_id, categorie=None, terme_recherche=None):
    conditions = ["site_id = %s"]
    params = [site_id]

    if categorie and categorie != "Tous":
        conditions.append("categorie = %s")
        params.append(categorie)

    if terme_recherche:
        conditions.append("nom ILIKE %s")
        params.append(f"%{terme_recherche}%")

    requete = f"""
        SELECT id, nom, categorie, unite, prix_achat, prix_vente,
               quantite_stock, seuil_alerte, fournisseur_id
        FROM articles
        WHERE {' AND '.join(conditions)}
        ORDER BY nom
    """
    return Database.fetch_all(requete, params)


def lister_categories(site_id):
    resultats = Database.fetch_all(
        "SELECT DISTINCT categorie FROM articles WHERE site_id = %s AND categorie IS NOT NULL ORDER BY categorie",
        (site_id,),
    )
    return [r["categorie"] for r in resultats]


def creer_article(site_id, nom, categorie, unite, prix_achat, prix_vente,
                   quantite_initiale, seuil_alerte, fournisseur_id=None):
    if not nom.strip():
        raise ValueError("Le nom de l'article est obligatoire.")
    if prix_vente <= 0:
        raise ValueError("Le prix de vente doit être supérieur à 0.")
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


def modifier_article(article_id, nom, categorie, unite, prix_achat, prix_vente, seuil_alerte, fournisseur_id=None):
    if not nom.strip():
        raise ValueError("Le nom de l'article est obligatoire.")
    if prix_vente <= 0:
        raise ValueError("Le prix de vente doit être supérieur à 0.")

    Database.execute(
        """
        UPDATE articles
        SET nom = %s, categorie = %s, unite = %s,
            prix_achat = %s, prix_vente = %s, seuil_alerte = %s, fournisseur_id = %s
        WHERE id = %s
        """,
        (nom.strip(), categorie, unite, prix_achat, prix_vente, seuil_alerte, fournisseur_id, article_id),
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


def lister_fournisseurs():
    return Database.fetch_all("SELECT id, nom FROM fournisseurs ORDER BY nom")
