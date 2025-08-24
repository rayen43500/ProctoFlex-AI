# 🚀 Guide de Démarrage Rapide - ProctoFlex AI

## 📋 Prérequis

- **Python 3.9+** installé
- **Node.js 18+** installé
- **PostgreSQL 13+** installé et en cours d'exécution
- **Git** installé

## 🏗️ Structure du Projet

```
proctoflex-ai/
├── backend/           # API FastAPI + IA
├── frontend/          # Interface admin React
├── desktop/           # Application Electron
├── docs/              # Documentation
├── docker-compose.yml # Orchestration Docker
└── README.md
```

## ⚡ Démarrage Rapide (5 minutes)

### 1. Cloner et Installer

```bash
# Cloner le projet
git clone <repository-url>
cd proctoflex-ai

# Installer les dépendances backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Installer les dépendances frontend
cd ../frontend
npm install

# Installer les dépendances desktop
cd ../desktop
npm install
```

### 2. Configuration Base de Données

```bash
# Créer la base de données
psql -U postgres
CREATE DATABASE proctoflex_db;
CREATE USER proctoflex_user WITH PASSWORD 'proctoflex_password';
GRANT ALL PRIVILEGES ON DATABASE proctoflex_db TO proctoflex_user;
\q
```

### 3. Variables d'Environnement

Créer un fichier `.env` dans le dossier `backend/` :

```env
DATABASE_URL=postgresql://proctoflex_user:proctoflex_password@localhost/proctoflex_db
SECRET_KEY=votre-cle-secrete-changez-en-production
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080
```

### 4. Lancer les Services

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2: Frontend Admin
cd frontend
npm run dev

# Terminal 3: Application Desktop
cd desktop
npm run dev
```

### 5. Accéder aux Services

- **Backend API**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs
- **Frontend Admin**: http://localhost:3000
- **Application Desktop**: Se lance automatiquement

## 🐳 Alternative Docker (Recommandé)

```bash
# Lancer tous les services
docker-compose up -d

# Vérifier l'état
docker-compose ps

# Logs en temps réel
docker-compose logs -f
```

## 🔐 Premier Utilisateur

1. Accéder à http://localhost:3000
2. Cliquer sur "Créer un compte"
3. Remplir le formulaire d'inscription
4. Se connecter avec les identifiants

## 📱 Test de l'Application Desktop

1. Lancer l'application Electron
2. Se connecter avec les mêmes identifiants
3. Tester la reconnaissance faciale
4. Vérifier les permissions webcam/micro

## 🧪 Tests Automatisés

```bash
# Tests backend
cd backend
pytest

# Tests frontend
cd frontend
npm test

# Tests desktop
cd desktop
npm test
```

## 🚨 Dépannage Courant

### Erreur de connexion base de données
- Vérifier que PostgreSQL est en cours d'exécution
- Vérifier les identifiants dans `.env`
- Vérifier que la base existe

### Erreur de permissions webcam
- Vérifier les permissions du navigateur
- Redémarrer l'application
- Vérifier qu'aucune autre application n'utilise la webcam

### Erreur de build Electron
- Vérifier la version de Node.js (18+)
- Nettoyer `node_modules` et réinstaller
- Vérifier les dépendances système

## 📊 Monitoring

- **Backend**: http://localhost:8000/health
- **Base de données**: Utiliser pgAdmin ou DBeaver
- **Logs**: `docker-compose logs -f [service]`

## 🔧 Développement

### Structure des Branches
- `main`: Code stable
- `develop`: Développement en cours
- `feature/*`: Nouvelles fonctionnalités
- `hotfix/*`: Corrections urgentes

### Standards de Code
- **Backend**: Black + Flake8
- **Frontend**: ESLint + Prettier
- **Desktop**: ESLint + TypeScript strict

## 📞 Support

- **Documentation**: `/docs`
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## 🎯 Prochaines Étapes

1. **Sprint 1** (Semaines 1-3): Finaliser l'authentification et le verrouillage
2. **Sprint 2** (Semaines 4-6): Implémenter l'enregistrement multimédia
3. **Sprint 3** (Semaines 7-9): Développer le moteur IA
4. **Sprint 4** (Semaines 10-12): Tests et finalisation

---

**Bonne chance avec ProctoFlex AI ! 🚀**
