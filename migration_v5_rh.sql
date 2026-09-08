-- ============================================================
-- Migration : volet RH (employés, absences/congés, avances sur salaire)
-- + traçabilité des salaires dans les dépenses de la comptabilité.
-- À exécuter UNE SEULE FOIS sur une base déjà créée avec la version
-- précédente du script (sinon, inutile : une base neuve créée avec
-- creation_base_donnees.sql à jour a déjà tout ceci).
--
-- Usage :
--   psql -U postgres -d quincaillerie_franck -f migration_v5_rh.sql
-- ============================================================

CREATE TABLE IF NOT EXISTS employes (
    id SERIAL PRIMARY KEY,
    nom_complet VARCHAR(150) NOT NULL,
    poste VARCHAR(100),
    telephone VARCHAR(30),
    type_contrat VARCHAR(20) NOT NULL DEFAULT 'permanent'
        CHECK (type_contrat IN ('permanent', 'temporaire')),
    salaire_mensuel NUMERIC(12,2) NOT NULL DEFAULT 0,
    site_id INTEGER REFERENCES sites(id),
    date_embauche DATE,
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    date_creation TIMESTAMP NOT NULL DEFAULT NOW()
);

ALTER TABLE transactions ADD COLUMN IF NOT EXISTS employe_id INTEGER;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_transactions_employe'
    ) THEN
        ALTER TABLE transactions
            ADD CONSTRAINT fk_transactions_employe FOREIGN KEY (employe_id) REFERENCES employes(id);
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS absences_conges (
    id SERIAL PRIMARY KEY,
    employe_id INTEGER NOT NULL REFERENCES employes(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL CHECK (type IN ('absence', 'conge')),
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    motif VARCHAR(200),
    utilisateur_id INTEGER NOT NULL REFERENCES utilisateurs(id),
    date_creation TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_absences_conges_employe ON absences_conges(employe_id);

CREATE TABLE IF NOT EXISTS avances_salaire (
    id SERIAL PRIMARY KEY,
    employe_id INTEGER NOT NULL REFERENCES employes(id) ON DELETE CASCADE,
    montant NUMERIC(12,2) NOT NULL,
    motif VARCHAR(200),
    remboursee BOOLEAN NOT NULL DEFAULT FALSE,
    utilisateur_id INTEGER NOT NULL REFERENCES utilisateurs(id),
    date_avance TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_avances_salaire_employe ON avances_salaire(employe_id);
