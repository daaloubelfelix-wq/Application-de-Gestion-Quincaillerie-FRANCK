-- ============================================================
-- Migration : comptage d'inventaire physique (matin/soir), article par
-- article, avec écart signalé si de la marchandise manque.
-- À exécuter UNE SEULE FOIS sur une base déjà créée avec la version
-- précédente du script (sinon, inutile : une base neuve créée avec
-- creation_base_donnees.sql à jour a déjà cette table).
--
-- Usage :
--   psql -U postgres -d quincaillerie_franck -f migration_v8_inventaire.sql
-- ============================================================

CREATE TABLE IF NOT EXISTS comptages_stock (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    utilisateur_id INTEGER NOT NULL REFERENCES utilisateurs(id),
    moment VARCHAR(10) NOT NULL CHECK (moment IN ('matin', 'soir')),
    quantite_attendue INTEGER NOT NULL,
    quantite_comptee INTEGER NOT NULL,
    ecart INTEGER NOT NULL,
    date_comptage TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_comptages_stock_article ON comptages_stock(article_id);
CREATE INDEX IF NOT EXISTS idx_comptages_stock_date ON comptages_stock(date_comptage);
