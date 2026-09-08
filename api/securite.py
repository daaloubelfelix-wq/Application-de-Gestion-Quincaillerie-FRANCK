"""
Authentification et jetons pour l'API mobile.
Accès en lecture seule, réservé au rôle "responsable" — les agents ne
peuvent pas se connecter depuis le mobile, même avec un mot de passe correct.

Un jeton JWT est délivré à la connexion (voir /api/connexion) et doit être
renvoyé dans l'en-tête "Authorization: Bearer <jeton>" pour chaque requête
suivante. Le jeton expire après quelques heures (voir config.ini, [api]).
"""

import configparser
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Header, HTTPException, status

_DOSSIER_PROJET = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CHEMIN_CONFIG = os.path.join(_DOSSIER_PROJET, "config.ini")

ALGORITHME = "HS256"


def _configuration_api():
    if not os.path.exists(_CHEMIN_CONFIG):
        raise RuntimeError(
            "Fichier config.ini introuvable. Copiez config.example.ini vers "
            "config.ini et renseignez la section [api] avant de démarrer le "
            "serveur mobile."
        )

    lecteur = configparser.ConfigParser()
    lecteur.read(_CHEMIN_CONFIG, encoding="utf-8")
    if not lecteur.has_section("api"):
        raise RuntimeError(
            "Section [api] absente de config.ini. Ajoutez une clé secrète "
            "(voir config.example.ini) avant de démarrer le serveur mobile."
        )

    section = lecteur["api"]
    return {
        "secret_key": section.get("secret_key"),
        "duree_session_heures": section.getint("duree_session_heures", fallback=12),
    }


def creer_jeton(utilisateur):
    config = _configuration_api()
    expiration = datetime.now(timezone.utc) + timedelta(hours=config["duree_session_heures"])
    charge = {
        "sub": str(utilisateur["id"]),
        "nom_complet": utilisateur["nom_complet"],
        "role": utilisateur["role"],
        "exp": expiration,
    }
    return jwt.encode(charge, config["secret_key"], algorithm=ALGORITHME)


def verifier_jeton(authorization: str = Header(None)):
    """
    Dépendance FastAPI : vérifie le jeton envoyé dans l'en-tête Authorization
    et retourne les informations qu'il contient (id, nom_complet, role).
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Connexion requise.")

    jeton = authorization.removeprefix("Bearer ").strip()
    config = _configuration_api()
    try:
        charge = jwt.decode(jeton, config["secret_key"], algorithms=[ALGORITHME])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session expirée, reconnectez-vous.")
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Jeton invalide.")

    if charge.get("role") != "responsable":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Accès réservé au responsable.")

    return charge
