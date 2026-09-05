"""
Routes de l'API mobile — lecture seule, réservée au responsable.
Réutilise directement la logique métier de modules/ (aucune requête SQL
dupliquée) : c'est la même base de données que l'application de bureau.
"""

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from database import Database
from modules.auth import authentifier
from modules.comptabilite import totaux_du_jour
from modules.articles import articles_en_alerte
from modules.rapports import totaux_periode, produits_plus_vendus
from api.securite import creer_jeton, verifier_jeton

routeur = APIRouter(prefix="/api")


class IdentifiantsConnexion(BaseModel):
    identifiant: str
    mot_de_passe: str


@routeur.post("/connexion")
def connexion(donnees: IdentifiantsConnexion):
    try:
        utilisateur = authentifier(donnees.identifiant, donnees.mot_de_passe)
    except ConnectionError as erreur:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(erreur))
    except ValueError as erreur:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(erreur))

    if utilisateur["role"] != "responsable":
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Cet accès est réservé au responsable.",
        )

    return {
        "jeton": creer_jeton(utilisateur),
        "nom_complet": utilisateur["nom_complet"],
    }


@routeur.get("/sites")
def sites(_utilisateur=Depends(verifier_jeton)):
    return Database.fetch_all("SELECT id, nom FROM sites ORDER BY nom")


@routeur.get("/tableau-de-bord")
def tableau_de_bord(site_id: Optional[int] = None, _utilisateur=Depends(verifier_jeton)):
    totaux = totaux_du_jour(site_id)
    alertes = articles_en_alerte(site_id)
    return {
        "recettes_jour": totaux["recettes"],
        "depenses_jour": totaux["depenses"],
        "solde_jour": totaux["solde_net"],
        "nombre_alertes": len(alertes),
        "alertes": alertes[:10],
    }


@routeur.get("/rapports")
def rapports(periode: str = "semaine", site_id: Optional[int] = None, _utilisateur=Depends(verifier_jeton)):
    aujourd_hui = date.today()
    if periode == "mois":
        date_debut = aujourd_hui.replace(day=1)
    elif periode == "30jours":
        date_debut = aujourd_hui - timedelta(days=30)
    else:
        periode = "semaine"
        date_debut = aujourd_hui - timedelta(days=aujourd_hui.weekday())

    totaux = totaux_periode(date_debut, aujourd_hui, site_id)
    produits = produits_plus_vendus(date_debut, aujourd_hui, site_id)

    return {
        "periode": periode,
        "total_ventes_ttc": totaux["total_ventes_ttc"],
        "marge_estimee": totaux["marge_estimee"],
        "produits_plus_vendus": produits,
    }
