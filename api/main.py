"""
Serveur API mobile — lecture seule, réservé au responsable.
Sert à la fois les données (JSON) et la page web mobile.

Démarrage (sur le PC serveur, celui qui héberge déjà PostgreSQL) :
    uvicorn api.main:app --host 0.0.0.0 --port 8000

Voir le README, section « Supervision mobile », pour le rendre accessible
depuis Internet via un tunnel chiffré (cloudflared) sans exposer directement
la box Internet de la boutique.
"""

import os

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.routes import routeur

app = FastAPI(title="Ets Quincaillerie Franck — Supervision mobile")
app.include_router(routeur)

_DOSSIER_STATIQUE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/assets", StaticFiles(directory=_DOSSIER_STATIQUE), name="assets")


@app.get("/")
def page_mobile():
    return FileResponse(os.path.join(_DOSSIER_STATIQUE, "index.html"))
