-- ============================================================
-- Migration : traçabilité des changements de prix des articles
-- (qui a changé le prix d'achat/vente, quand, ancien montant -> nouveau
-- montant). Sans cette table, un prix modifié sans laisser de trace
-- ouvre la porte au vol.
-- À exécuter UNE SEULE FOIS sur une base déjà créée avec la version
-- précédente du script (sinon, inutile : une base neuve créée avec
-- creation_base_donnees.sql à jour a déjà cette table).
--
-- Usage :
--   psql -U postgres -d quincaillerie_franck -f migration_v4_historique_prix.sql
-- ============================================================

CREATE TABLE IF NOT EXISTS historique_prix_articles (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    utilisateur_id INTEGER NOT NULL REFERENCES utilisateurs(id),
    ancien_prix_achat NUMERIC(12,2) NOT NULL,
    nouveau_prix_achat NUMERIC(12,2) NOT NULL,
    ancien_prix_vente NUMERIC(12,2) NOT NULL,
    nouveau_prix_vente NUMERIC(12,2) NOT NULL,
    date_modification TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_historique_prix_article ON historique_prix_articles(article_id);
