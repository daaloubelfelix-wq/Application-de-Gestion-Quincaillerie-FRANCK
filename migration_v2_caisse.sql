-- ============================================================
-- Migration : sépare commande (comptabilité) et encaissement (caisse)
-- À exécuter UNE SEULE FOIS sur une base déjà créée avec l'ancienne
-- version de creation_base_donnees.sql (sinon, inutile : une nouvelle
-- base créée avec le script à jour a déjà tout ceci).
--
-- Usage :
--   psql -U postgres -d quincaillerie_franck -f migration_v2_caisse.sql
-- ============================================================

ALTER TABLE ventes
    ADD COLUMN IF NOT EXISTS statut VARCHAR(20) NOT NULL DEFAULT 'payee'
        CHECK (statut IN ('en_attente', 'payee', 'annulee')),
    ADD COLUMN IF NOT EXISTS utilisateur_caisse_id INTEGER REFERENCES utilisateurs(id),
    ADD COLUMN IF NOT EXISTS date_encaissement TIMESTAMP;

-- Les ventes déjà enregistrées avant cette migration sont considérées
-- payées (elles avaient déjà créé une recette à l'époque) :
UPDATE ventes SET statut = 'payee', date_encaissement = date_vente
WHERE statut IS DISTINCT FROM 'payee' AND id IN (
    SELECT vente_id FROM transactions WHERE vente_id IS NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ventes_statut ON ventes(statut);
