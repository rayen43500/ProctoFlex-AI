-- Migration pour ajouter les nouveaux champs à la table exams
-- Ce script doit être exécuté sur une base de données existante

-- Ajouter les nouveaux champs à la table exams
ALTER TABLE exams 
ADD COLUMN IF NOT EXISTS instructions TEXT,
ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'draft',
ADD COLUMN IF NOT EXISTS pdf_path VARCHAR(500),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Modifier les colonnes start_time et end_time pour les rendre optionnelles
ALTER TABLE exams 
ALTER COLUMN start_time DROP NOT NULL,
ALTER COLUMN end_time DROP NOT NULL;

-- Créer un trigger pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Appliquer le trigger à la table exams
DROP TRIGGER IF EXISTS update_exams_updated_at ON exams;
CREATE TRIGGER update_exams_updated_at
    BEFORE UPDATE ON exams
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Mettre à jour les examens existants avec un statut par défaut
UPDATE exams SET status = 'draft' WHERE status IS NULL;

-- Message de confirmation
SELECT 'Migration des champs d\'examen terminée avec succès!' as message;
