# 🚀 ProctoFlex AI - Guide de Démarrage Rapide

## 📋 Prérequis

- **Docker** et **Docker Compose** installés
- **Node.js 18+** (pour le frontend et desktop)
- **Python 3.11+** (pour le backend)
- **PostgreSQL 15+** (optionnel, Docker fournit une instance)

## ⚡ Démarrage Ultra-Rapide (5 minutes)

### 1. Cloner et Configurer
```bash
git clone <repository-url>
cd proctoflex-ai
```

### 2. Démarrer avec Docker (Recommandé)
```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier le statut
docker-compose ps
```

### 3. Accéder aux Services
- **Backend API** : http://localhost:8000
- **Frontend Web** : http://localhost:3000
- **Base de données** : localhost:5432

## 🔧 Démarrage Manuel (Développement)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-simple.txt
python main_simple.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Desktop App
```bash
cd desktop
npm install
npm run dev
```

## 🐳 Configuration Docker Avancée

### Services Disponibles
- **postgres** : Base de données PostgreSQL
- **redis** : Cache et sessions
- **backend** : API FastAPI
- **frontend** : Interface web React

### Variables d'Environnement
```bash
# Backend
DATABASE_URL=postgresql://root:root@postgres:5432/proctoflex
REDIS_URL=redis://redis:6379
SECRET_KEY=your-secret-key

# Frontend
VITE_API_URL=http://localhost:8000
```

## 🧪 Tests

### Test Complet du Système
```bash
python scripts/test/test-complete-system.py
```

### Tests Individuels
```bash
# Backend
cd backend && python -m pytest

# Frontend
cd frontend && npm test

# Desktop
cd desktop && npm test
```

## 📦 Build et Déploiement

### Build Docker
```bash
# Build toutes les images
docker-compose build

# Build spécifique
docker-compose build backend
```

### Build Applications
```bash
# Frontend
cd frontend && npm run build

# Desktop (Windows)
cd desktop && npm run build:win

# Desktop (macOS)
cd desktop && npm run build:mac

# Desktop (Linux)
cd desktop && npm run build:linux
```

## 🔍 Dépannage

### Problèmes Courants

#### 1. Port déjà utilisé
```bash
# Vérifier les ports utilisés
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000

# Arrêter les services
docker-compose down
```

#### 2. Erreurs de dépendances
```bash
# Nettoyer et reconstruire
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

#### 3. Problèmes de base de données
```bash
# Réinitialiser la base
docker-compose down -v
docker volume prune
docker-compose up -d
```

### Logs
```bash
# Tous les services
docker-compose logs

# Service spécifique
docker-compose logs backend
docker-compose logs postgres
```

## 🚀 Production

### Configuration Production
```bash
# Utiliser le fichier de production
docker-compose -f docker-compose.prod.yml up -d
```

### Variables d'Environnement Production
```bash
# .env.production
DATABASE_URL=postgresql://user:password@db:5432/proctoflex
REDIS_URL=redis://redis:6379
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com
```

## 📚 Documentation Complète

- [Manuel Administrateur](docs/ADMIN_MANUAL.md)
- [Manuel Étudiant](docs/STUDENT_MANUAL.md)
- [Architecture Technique](docs/architecture.md)
- [API Documentation](docs/api.md)

## 🆘 Support

- **Issues** : [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation** : [Wiki](https://github.com/your-repo/wiki)
- **Email** : support@proctoflex.ai

---

**ProctoFlex AI** - Surveillance intelligente pour examens en ligne
*Développé par l'Université de Monastir - ESPRIM*
