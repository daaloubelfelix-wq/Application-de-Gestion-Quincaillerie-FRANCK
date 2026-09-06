"""
Comptage d'inventaire physique — réservé à l'agent stock (matin/soir).
La comptabilité ne voit jamais les quantités en stock : elle enregistre
ce qui a déjà été validé à la caisse, ce n'est pas son problème (voir
modules/ventes.py::rechercher_articles). Ici, on compare ce que
l'agent stock compte physiquement à ce que le système attend
(articles.quantite_stock au moment du comptage) — un écart négatif
signale de la marchandise manquante.
"""

from datetime import date
from database import Database

MOMENTS = [("matin", "Matin"), ("soir", "Soir")]


def enregistrer_comptage(article_id, moment, quantite_comptee, utilisateur_id):
    if moment not in ("matin", "soir"):
        raise ValueError("Moment invalide (matin ou soir).")
    if quantite_comptee < 0:
        raise ValueError("La quantité comptée ne peut pas être négative.")

    with Database.transaction() as cur:
        cur.execute("SELECT quantite_stock FROM articles WHERE id = %s", (article_id,))
        article = cur.fetchone()
        if article is None:
            raise ValueError("Article introuvable.")

        quantite_attendue = article["quantite_stock"]
        ecart = quantite_comptee - quantite_attendue

        cur.execute(
            """
            INSERT INTO comptages_stock
                (article_id, utilisateur_id, moment, quantite_attendue, quantite_comptee, ecart)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (article_id, utilisateur_id, moment, quantite_attendue, quantite_comptee, ecart),
        )
    return ecart


def statut_inventaire_jour(site_id):
    """
    Pour le tableau de bord de l'agent stock : vert si tous les
    comptages du jour sont sans écart (ou aucun comptage fait), rouge
    dès qu'un seul écart est détecté, avec le détail des articles en
    cause.
    """
    aujourd_hui = date.today()
    comptages = Database.fetch_all(
        """
        SELECT c.ecart, a.nom
        FROM comptages_stock c
        JOIN articles a ON a.id = c.article_id
        WHERE a.site_id = %s AND c.date_comptage::date = %s
        ORDER BY c.date_comptage DESC
        """,
        (site_id, aujourd_hui),
    )
    ecarts = [c for c in comptages if c["ecart"] != 0]
    return {
        "nombre_comptages": len(comptages),
        "en_ordre": len(ecarts) == 0,
        "ecarts": ecarts,
    }


def comptages_du_jour(site_id, moment=None):
    condition_moment = "AND c.moment = %s" if moment else ""
    params = [site_id, date.today()]
    if moment:
        params.append(moment)
    return Database.fetch_all(
        f"""
        SELECT c.id, c.moment, c.quantite_attendue, c.quantite_comptee, c.ecart, c.date_comptage,
               a.nom AS article_nom, u.nom_complet AS enregistre_par
        FROM comptages_stock c
        JOIN articles a ON a.id = c.article_id
        JOIN utilisateurs u ON u.id = c.utilisateur_id
        WHERE a.site_id = %s AND c.date_comptage::date = %s {condition_moment}
        ORDER BY c.date_comptage DESC
        """,
        params,
    )


def historique_comptages(site_id=None, date_debut=None, date_fin=None, limite=200):
    """Pour le responsable : historique des comptages, tous sites ou un
    site précis, utilisé lors des réunions hebdomadaires/mensuelles."""
    conditions = []
    params = []
    if site_id is not None:
        conditions.append("a.site_id = %s")
        params.append(site_id)
    if date_debut is not None:
        conditions.append("c.date_comptage::date >= %s")
        params.append(date_debut)
    if date_fin is not None:
        conditions.append("c.date_comptage::date <= %s")
        params.append(date_fin)
    clause_where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    params.append(limite)

    return Database.fetch_all(
        f"""
        SELECT c.id, c.moment, c.quantite_attendue, c.quantite_comptee, c.ecart, c.date_comptage,
               a.nom AS article_nom, s.nom AS site_nom, u.nom_complet AS enregistre_par
        FROM comptages_stock c
        JOIN articles a ON a.id = c.article_id
        JOIN sites s ON s.id = a.site_id
        JOIN utilisateurs u ON u.id = c.utilisateur_id
        {clause_where}
        ORDER BY c.date_comptage DESC
        LIMIT %s
        """,
        params,
    )
