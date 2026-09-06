"""
Rapports pour le responsable.
Filtrable par site (ou tous les sites) et par période.

Ne compte que les commandes réellement encaissées (statut 'payee') — une
commande enregistrée par la comptabilité mais pas encore payée à la caisse
n'apparaît pas dans le chiffre d'affaires, cohérent avec les recettes du
tableau de bord (voir modules/comptabilite.py et modules/ventes.py).
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
               COALESCE(SUM(sous_total_ht), 0) AS total_ht,
               COUNT(*) AS nombre_ventes
        FROM ventes
        WHERE statut = 'payee' AND date_vente::date BETWEEN %s AND %s {condition_site}
        """,
        params,
    )

    return {
        "total_ventes_ttc": float(ventes["total_ventes"]),
        "total_ventes_ht": float(ventes["total_ht"]),
        "nombre_ventes": ventes["nombre_ventes"],
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
        WHERE statut = 'payee' AND date_vente::date BETWEEN %s AND %s {condition_site}
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
        WHERE v.statut = 'payee' AND v.date_vente::date BETWEEN %s AND %s {condition_site}
        GROUP BY a.nom
        ORDER BY quantite_vendue DESC
        LIMIT %s
        """,
        params,
    )
