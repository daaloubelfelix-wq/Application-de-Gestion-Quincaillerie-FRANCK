-- ============================================================
-- Migration : traçabilité des modifications d'article autres que le
-- prix (nom, unité, seuil d'alerte) — sans quoi impossible de savoir
-- qui a changé un seuil ou renommé un article, et quand.
-- À exécuter UNE SEULE FOIS sur une base déjà créée avec la version
-- précédente du script (sinon, inutile : une base neuve créée avec
-- creation_base_donnees.sql à jour a déjà cette table).
--
-- Usage :
--   psql -U postgres -d quincaillerie_franck -f migration_v7_historique_articles.sql
-- ============================================================

CREATE TABLE IF NOT EXISTS historique_modifications_articles (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    utilisateur_id INTEGER NOT NULL REFERENCES utilisateurs(id),
    champ VARCHAR(30) NOT NULL,
    ancienne_valeur VARCHAR(200),
    nouvelle_valeur VARCHAR(200),
    date_modification TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_historique_modif_article ON historique_modifications_articles(article_id);
