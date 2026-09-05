"""
Connexion centralisée à la base de données PostgreSQL.
Tous les postes (magasin, comptoir, bureau du responsable) se connectent
au même serveur sur le réseau local.
"""

import psycopg2
import psycopg2.extras

# ------------------------------------------------------------
# Paramètres de connexion — à ajuster selon le poste serveur
# ------------------------------------------------------------
DB_CONFIG = {
    "host": "192.168.1.10",   # adresse IP du poste serveur sur le réseau local
    "port": 5432,
    "dbname": "quincaillerie_franck",
    "user": "quincaillerie_user",
    "password": "changer_ce_mot_de_passe",
}


class Database:
    """Gère une connexion unique réutilisable vers PostgreSQL."""

    _connection = None

    @classmethod
    def get_connection(cls):
        if cls._connection is None or cls._connection.closed:
            try:
                cls._connection = psycopg2.connect(**DB_CONFIG)
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
