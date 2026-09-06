-- ============================================================
-- Migration : invite à changer le mot de passe à la première connexion
-- + écran "Paramètres" (identifiant et mot de passe réunis).
-- À exécuter UNE SEULE FOIS sur une base déjà créée avec la version
-- précédente du script (sinon, inutile : une base neuve créée avec
-- creation_base_donnees.sql à jour a déjà cette colonne).
--
-- Usage :
--   psql -U postgres -d quincaillerie_franck -f migration_v6_parametres.sql
-- ============================================================

ALTER TABLE utilisateurs
    ADD COLUMN IF NOT EXISTS doit_changer_mot_de_passe BOOLEAN NOT NULL DEFAULT TRUE;
