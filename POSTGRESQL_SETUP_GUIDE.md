# 🗄️ Guide de Configuration PostgreSQL pour ProctoFlex

## 📋 Vue d'ensemble

ProctoFlex utilise PostgreSQL comme base de données principale pour stocker :
- 👥 Utilisateurs (étudiants, instructeurs, administrateurs)
- 📝 Examens avec fichiers PDF
- 🎯 Sessions d'examen
- 🚨 Alertes de sécurité
- 📊 Données de surveillance

## 🚀 Démarrage Rapide

### Option 1 : Docker (Recommandé)

```bash
# 1. Démarrer PostgreSQL avec Docker
docker-compose up postgres -d

# 2. Vérifier que PostgreSQL fonctionne
docker-compose logs postgres

# 3. Configurer la base de données
cd backend
python setup_database.py

# 4. Vérifier la configuration
python check_database.py
```

### Option 2 : Installation Locale

#### Windows
```bash
# 1. Télécharger PostgreSQL depuis https://www.postgresql.org/download/windows/
# 2. Installer avec les paramètres par défaut
# 3. Créer la base de données
createdb proctoflex

# 4. Configurer la base
cd backend
python setup_database.py
```

#### Linux/macOS
```bash
# 1. Installer PostgreSQL
sudo apt-get install postgresql postgresql-contrib  # Ubuntu/Debian
brew install postgresql                              # macOS

# 2. Démarrer le service
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS

# 3. Créer la base de données
sudo -u postgres createdb proctoflex

# 4. Configurer la base
cd backend
python setup_database.py
```

## ⚙️ Configuration

### 1. Variables d'Environnement

Créez un fichier `.env` dans le dossier `backend/` :

```bash
# Base de données PostgreSQL
DATABASE_URL=postgresql://root:root@localhost:5432/proctoflex
DATABASE_TEST_URL=postgresql://root:root@localhost:5432/proctoflex_test

# Sécurité
SECRET_KEY=your-secret-key-change-in-production-please-use-a-strong-random-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Serveur
HOST=0.0.0.0
PORT=8000
DEBUG=true

# CORS
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:8080"]
```

### 2. Structure de la Base de Données

```sql
-- Table des utilisateurs
CREATE TABLE users (
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

-- Table des examens
CREATE TABLE exams (
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

-- Table des sessions d'examen
CREATE TABLE exam_sessions (
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

-- Table des alertes de sécurité
CREATE TABLE security_alerts (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES exam_sessions(id),
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) DEFAULT 'medium',
    description TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_resolved BOOLEAN DEFAULT FALSE
);
```

## 🔧 Scripts de Configuration

### 1. Configuration Automatique
```bash
cd backend
python setup_database.py
```

Ce script :
- ✅ Teste la connexion PostgreSQL
- ✅ Crée toutes les tables
- ✅ Exécute les migrations
- ✅ Vérifie la configuration

### 2. Vérification de la Base
```bash
cd backend
python check_database.py
```

Ce script :
- ✅ Vérifie la connexion
- ✅ Liste les tables
- ✅ Compte les données
- ✅ Vérifie les nouveaux champs

### 3. Migration des Champs
```bash
# Si vous avez une base existante
psql proctoflex < migrations/add_exam_fields.sql
```

## 🧪 Tests et Validation

### 1. Test de Connexion
```bash
# Test rapide
psql proctoflex -c "SELECT version();"

# Test avec Python
cd backend
python -c "from app.core.database import engine; print('✅ Connexion OK')"
```

### 2. Test du Système d'Examens
```bash
cd backend
python test_exam_system.py
```

### 3. Test de l'API
```bash
# Démarrer le serveur
python main.py

# Dans un autre terminal
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/exams
```

## 📊 Gestion des Données

### 1. Sauvegarde
```bash
# Sauvegarde complète
pg_dump proctoflex > backup_$(date +%Y%m%d).sql

# Sauvegarde avec Docker
docker exec proctoflex-postgres pg_dump -U root proctoflex > backup.sql
```

### 2. Restauration
```bash
# Restauration
psql proctoflex < backup_20231201.sql

# Avec Docker
docker exec -i proctoflex-postgres psql -U root proctoflex < backup.sql
```

### 3. Nettoyage
```bash
# Supprimer les données de test
psql proctoflex -c "DELETE FROM exams WHERE title LIKE '%Test%';"

# Réinitialiser la base
psql proctoflex -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
python setup_database.py
```

## 🔍 Monitoring et Logs

### 1. Logs PostgreSQL
```bash
# Docker
docker-compose logs postgres

# Local
tail -f /var/log/postgresql/postgresql.log
```

### 2. Monitoring des Performances
```sql
-- Connexions actives
SELECT * FROM pg_stat_activity;

-- Taille des tables
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Statistiques des requêtes
SELECT * FROM pg_stat_user_tables;
```

## 🚨 Dépannage

### Problèmes Courants

#### 1. Erreur de Connexion
```
❌ Erreur: connection to server at "localhost" (127.0.0.1), port 5432 failed
```

**Solutions :**
- Vérifier que PostgreSQL est démarré
- Vérifier le port (5432 par défaut)
- Vérifier les credentials dans `.env`

#### 2. Base de Données Inexistante
```
❌ Erreur: database "proctoflex" does not exist
```

**Solutions :**
```bash
createdb proctoflex
# Ou avec Docker
docker exec proctoflex-postgres createdb -U root proctoflex
```

#### 3. Tables Manquantes
```
❌ Erreur: relation "exams" does not exist
```

**Solutions :**
```bash
python setup_database.py
# Ou
psql proctoflex < init.sql
```

#### 4. Permissions Insuffisantes
```
❌ Erreur: permission denied for table users
```

**Solutions :**
```bash
# Accorder les permissions
psql proctoflex -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO root;"
```

### Commandes Utiles

```bash
# Connexion à PostgreSQL
psql proctoflex

# Lister les bases de données
psql -l

# Lister les tables
\dt

# Décrire une table
\d exams

# Quitter
\q
```

## 🔐 Sécurité

### 1. Configuration Sécurisée
```bash
# Changer le mot de passe par défaut
psql -c "ALTER USER root PASSWORD 'nouveau_mot_de_passe_fort';"

# Limiter les connexions
# Modifier pg_hba.conf pour restreindre l'accès
```

### 2. Sauvegarde Sécurisée
```bash
# Chiffrer les sauvegardes
pg_dump proctoflex | gzip | openssl enc -aes-256-cbc -out backup.sql.gz.enc
```

## 📈 Performance

### 1. Optimisation
```sql
-- Créer des index pour améliorer les performances
CREATE INDEX idx_exams_instructor_id ON exams(instructor_id);
CREATE INDEX idx_exams_status ON exams(status);
CREATE INDEX idx_exam_sessions_exam_id ON exam_sessions(exam_id);
```

### 2. Maintenance
```sql
-- Analyser les tables
ANALYZE;

-- Nettoyer les statistiques
VACUUM ANALYZE;
```

## 🎯 Prochaines Étapes

1. ✅ **Configuration terminée** - Base de données prête
2. 🚀 **Démarrer l'application** - `python main.py`
3. 🧪 **Tester le système** - `python test_exam_system.py`
4. 🌐 **Accéder à l'interface** - http://localhost:3000
5. 📝 **Créer des examens** - Interface web ou API

## 📞 Support

En cas de problème :
1. Vérifier les logs : `docker-compose logs postgres`
2. Tester la connexion : `python check_database.py`
3. Consulter la documentation PostgreSQL
4. Vérifier la configuration dans `.env`

---

🎉 **Votre base de données PostgreSQL ProctoFlex est maintenant configurée et prête à l'emploi !**
