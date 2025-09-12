-- Initialisation de la base de données ProctoFlex AI
-- Ce script est exécuté automatiquement lors du premier démarrage du conteneur PostgreSQL

-- Création de la base de données de test si elle n'existe pas
SELECT 'CREATE DATABASE proctoflex_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'proctoflex_test')\gexec

-- Connexion à la base de données principale
\c proctoflex;

-- Extension pour UUID (si nécessaire)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Extension pour les fonctions de cryptographie
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Création des tables principales
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'student',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS exams (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    duration_minutes INTEGER NOT NULL,
    instructions TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    student_id INTEGER REFERENCES users(id),
    instructor_id INTEGER REFERENCES users(id),
    allowed_apps TEXT,
    allowed_domains TEXT,
    pdf_path VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS exam_sessions (
    id SERIAL PRIMARY KEY,
    exam_id INTEGER REFERENCES exams(id),
    student_id INTEGER REFERENCES users(id),
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'active',
    video_path VARCHAR(500),
    audio_path VARCHAR(500),
    screen_captures TEXT
);

CREATE TABLE IF NOT EXISTS security_alerts (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES exam_sessions(id),
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) DEFAULT 'medium',
    description TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_resolved BOOLEAN DEFAULT FALSE
);

-- Création des index pour optimiser les performances
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_exams_student_id ON exams(student_id);
CREATE INDEX IF NOT EXISTS idx_exams_instructor_id ON exams(instructor_id);
CREATE INDEX IF NOT EXISTS idx_exam_sessions_exam_id ON exam_sessions(exam_id);
CREATE INDEX IF NOT EXISTS idx_exam_sessions_student_id ON exam_sessions(student_id);
CREATE INDEX IF NOT EXISTS idx_security_alerts_session_id ON security_alerts(session_id);
CREATE INDEX IF NOT EXISTS idx_security_alerts_timestamp ON security_alerts(timestamp);

-- Insertion d'un utilisateur administrateur par défaut
INSERT INTO users (email, username, full_name, hashed_password, role, is_active)
VALUES (
    'admin@proctoflex.ai',
    'admin',
    'Administrateur ProctoFlex',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J8K8K8K8K', -- Mot de passe: admin123
    'admin',
    TRUE
) ON CONFLICT (email) DO NOTHING;

-- Insertion d'un utilisateur étudiant de test
INSERT INTO users (email, username, full_name, hashed_password, role, is_active)
VALUES (
    'student@test.com',
    'student1',
    'Étudiant Test',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J8K8K8K', -- Mot de passe: student123
    'student',
    TRUE
) ON CONFLICT (email) DO NOTHING;

-- Message de confirmation
SELECT 'Base de données ProctoFlex AI initialisée avec succès!' as message;
