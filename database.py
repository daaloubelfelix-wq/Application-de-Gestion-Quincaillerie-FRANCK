"""
Connexion centralisée à la base de données PostgreSQL.
Tous les postes (magasin, comptoir, bureau du responsable) se connectent
au même serveur sur le réseau local.

Les paramètres de connexion viennent de config.ini (jamais versionné, voir
config.example.ini) pour éviter d'avoir un mot de passe écrit dans le code
et de devoir modifier un fichier Python sur chaque poste.
"""

import configparser
import os
from contextlib import contextmanager

import psycopg2
import psycopg2.extras

_DOSSIER_PROJET = os.path.dirname(os.path.abspath(__file__))
_CHEMIN_CONFIG = os.path.join(_DOSSIER_PROJET, "config.ini")


def _charger_configuration():
    if not os.path.exists(_CHEMIN_CONFIG):
        raise FileNotFoundError(
            "Fichier config.ini introuvable. "
            "Copiez config.example.ini vers config.ini puis renseignez "
            "les paramètres du serveur PostgreSQL."
        )

    lecteur = configparser.ConfigParser()
    lecteur.read(_CHEMIN_CONFIG, encoding="utf-8")
    section = lecteur["database"]
    return {
        "host": section.get("host"),
        "port": section.getint("port"),
        "dbname": section.get("dbname"),
        "user": section.get("user"),
        "password": section.get("password"),
    }


class Database:
    """Gère une connexion unique réutilisable vers PostgreSQL."""

    _connection = None

    @classmethod
    def get_connection(cls):
        if cls._connection is None or cls._connection.closed:
            try:
                cls._connection = psycopg2.connect(**_charger_configuration())
            except psycopg2.OperationalError as erreur:
                raise ConnectionError(
                    "Impossible de joindre le serveur. "
                    "Vérifiez que le poste serveur est allumé et connecté au réseau."
                ) from erreur
        return cls._connection

    @classmethod
    def fetch_one(cls, query, params=None):
        conn = cls.get_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params or ())
            return cur.fetchone()

    @classmethod
    def fetch_all(cls, query, params=None):
        conn = cls.get_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params or ())
            return cur.fetchall()

    @classmethod
    def execute(cls, query, params=None):
        conn = cls.get_connection()
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            conn.commit()
            return cur.rowcount

    @classmethod
    @contextmanager
    def transaction(cls):
        """
        Fournit un curseur pour exécuter plusieurs requêtes dans une seule
        transaction : soit toutes les écritures réussissent (commit), soit
        aucune n'est conservée (rollback) en cas d'erreur.

        Usage :
            with Database.transaction() as cur:
                cur.execute("INSERT INTO ...", (...))
                cur.execute("UPDATE ...", (...))
        """
        conn = cls.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
