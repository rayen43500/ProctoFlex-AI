-- Migration pour ajouter la table exam_students
-- Cette table permet d'assigner plusieurs étudiants à un examen

CREATE TABLE IF NOT EXISTS exam_students (
    id SERIAL PRIMARY KEY,
    exam_id INTEGER NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'assigned',
    UNIQUE(exam_id, student_id)
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_exam_students_exam_id ON exam_students(exam_id);
CREATE INDEX IF NOT EXISTS idx_exam_students_student_id ON exam_students(student_id);
CREATE INDEX IF NOT EXISTS idx_exam_students_status ON exam_students(status);

-- Supprimer l'ancienne colonne student_id de la table exams si elle existe
-- (Cette commande peut échouer si la colonne n'existe pas, c'est normal)
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'exams' AND column_name = 'student_id') THEN
        ALTER TABLE exams DROP COLUMN student_id;
    END IF;
END $$;
