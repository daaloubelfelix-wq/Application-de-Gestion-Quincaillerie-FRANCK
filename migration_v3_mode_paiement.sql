-- ============================================================
-- Migration : ajoute le mode de paiement à l'encaissement
-- (Espèces, Orange Money, MTN Mobile Money, Crédit client, Autre)
-- À exécuter UNE SEULE FOIS sur une base déjà créée avec la version
-- précédente du script (sinon, inutile : une base neuve créée avec
-- creation_base_donnees.sql à jour a déjà cette colonne).
--
-- Usage :
--   psql -U postgres -d quincaillerie_franck -f migration_v3_mode_paiement.sql
-- ============================================================

ALTER TABLE ventes
    ADD COLUMN IF NOT EXISTS mode_paiement VARCHAR(30)
        CHECK (mode_paiement IN ('especes', 'orange_money', 'mtn_momo', 'credit_client', 'autre'));
