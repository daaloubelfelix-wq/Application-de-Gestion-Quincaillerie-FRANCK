"""
Rapports pour le responsable.
Filtrable par site (ou tous les sites) et par période.
"""

from database import Database


def totaux_periode(date_debut, date_fin, site_id=None):
    condition_site = ""
    params = [date_debut, date_fin]
    if site_id is not None:
        condition_site = "AND site_id = %s"
        params.append(site_id)

    ventes = Database.fetch_one(
        f"""
        SELECT COALESCE(SUM(total_ttc), 0) AS total_ventes,
               COALESCE(SUM(sous_total_ht), 0) AS total_ht
        FROM ventes
        WHERE date_vente::date BETWEEN %s AND %s {condition_site}
        """,
        params,
    )

    marge = Database.fetch_one(
        f"""
        SELECT COALESCE(SUM((vl.prix_unitaire - a.prix_achat) * vl.quantite), 0) AS marge
        FROM ventes_lignes vl
        JOIN ventes v ON v.id = vl.vente_id
        JOIN articles a ON a.id = vl.article_id
        WHERE v.date_vente::date BETWEEN %s AND %s {condition_site}
        """,
        params,
    )

    return {
        "total_ventes_ttc": float(ventes["total_ventes"]),
        "total_ventes_ht": float(ventes["total_ht"]),
        "marge_estimee": float(marge["marge"]),
    }


def ventes_par_jour(date_debut, date_fin, site_id=None):
    condition_site = ""
    params = [date_debut, date_fin]
    if site_id is not None:
        condition_site = "AND site_id = %s"
        params.append(site_id)

    return Database.fetch_all(
        f"""
        SELECT date_vente::date AS jour, SUM(total_ttc) AS total
        FROM ventes
        WHERE date_vente::date BETWEEN %s AND %s {condition_site}
        GROUP BY jour
        ORDER BY jour
        """,
        params,
    )


def produits_plus_vendus(date_debut, date_fin, site_id=None, limite=10):
    condition_site = ""
    params = [date_debut, date_fin]
    if site_id is not None:
        condition_site = "AND v.site_id = %s"
        params.append(site_id)
    params.append(limite)

    return Database.fetch_all(
        f"""
        SELECT a.nom, SUM(vl.quantite) AS quantite_vendue
        FROM ventes_lignes vl
        JOIN ventes v ON v.id = vl.vente_id
        JOIN articles a ON a.id = vl.article_id
        WHERE v.date_vente::date BETWEEN %s AND %s {condition_site}
        GROUP BY a.nom
        ORDER BY quantite_vendue DESC
        LIMIT %s
        """,
        params,
    )
