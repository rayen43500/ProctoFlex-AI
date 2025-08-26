# 🎓 ProctoFlex AI - Système de Surveillance d'Examens

Un système complet de surveillance intelligente pour examens en ligne avec reconnaissance faciale, détection d'objets et monitoring en temps réel.

## 🚀 Démarrage Rapide

### Option 1: Démarrage Automatique (Recommandé)
```bash
# Double-cliquez sur le fichier
start_all.bat
```

### Option 2: Démarrage Manuel

#### Backend (API)
```bash
# Option A: Script automatique
start_backend.bat

# Option B: Manuel
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements-simple.txt
python main_simple.py
```

#### Desktop Application
```bash
# Option A: Script automatique
start_desktop.bat

# Option B: Manuel
cd desktop
npm install
npm run dev
```

## 📋 Prérequis

- **Python 3.13+** (installé automatiquement)
- **Node.js 18+** (installé automatiquement)
- **Git** (pour cloner le projet)

## 🏗️ Architecture

```
proctoflex-ai/
├── backend/                 # API FastAPI
│   ├── main_simple.py      # Serveur principal (version simplifiée)
│   ├── requirements-simple.txt # Dépendances Python
│   └── app/                # Modules de l'application
├── desktop/                # Application Electron
│   ├── src/renderer/       # Interface React
│   ├── main.ts            # Processus principal Electron
│   └── package.json       # Dépendances Node.js
├── frontend/               # Interface web admin
└── docker-compose.yml      # Configuration Docker
```

## 🌐 Services Disponibles

| Service | URL | Description |
|---------|-----|-------------|
| **Backend API** | http://localhost:8000 | API REST principale |
| **Documentation API** | http://localhost:8000/docs | Swagger UI |
| **Health Check** | http://localhost:8000/health | État du serveur |
| **Desktop App** | Electron Window | Application native |
| **Frontend Admin** | http://localhost:3000 | Interface web |

## 🔧 Configuration

### Variables d'Environnement Backend
```bash
# backend/.env
HOST=localhost
PORT=8000
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./proctoflex.db
```

### Configuration Desktop
```json
// desktop/package.json
{
  "scripts": {
    "dev": "concurrently \"npm run dev:renderer\" \"npm run dev:main\"",
    "dev:renderer": "vite",
    "dev:main": "tsc && electron ."
  }
}
```

## 📱 Fonctionnalités

### ✅ Implémentées
- [x] **Backend API** - FastAPI avec endpoints REST
- [x] **Desktop App** - Application Electron avec React
- [x] **Interface Moderne** - Design responsive avec Tailwind CSS
- [x] **Authentification** - Système de login simulé
- [x] **Dashboard** - Interface de surveillance
- [x] **Monitoring** - Surveillance des processus système
- [x] **Documentation** - API docs avec Swagger

### 🔄 En Développement
- [ ] **Reconnaissance Faciale** - OpenCV + face_recognition
- [ ] **Détection d'Objets** - YOLO integration
- [ ] **Base de Données** - PostgreSQL + Redis
- [ ] **WebSocket** - Communication temps réel
- [ ] **Notifications** - Alertes en temps réel

## 🛠️ Développement

### Structure du Code
```
backend/
├── app/
│   ├── api/v1/           # Endpoints API
│   ├── core/             # Configuration
│   ├── models/           # Modèles de données
│   └── ai/               # Services IA
└── main_simple.py        # Point d'entrée

desktop/
├── src/renderer/
│   ├── components/       # Composants React
│   ├── contexts/         # Contextes React
│   ├── styles/           # Styles CSS/SCSS
│   └── App.tsx          # Application principale
└── main.ts              # Processus Electron
```

### Scripts Utiles
```bash
# Backend
cd backend
python main_simple.py          # Démarrer le serveur
pip install -r requirements-simple.txt  # Installer dépendances

# Desktop
cd desktop
npm run dev                    # Mode développement
npm run build                  # Build production
npm run electron:build         # Build Electron
```

## 🔍 Dépannage

### Problèmes Courants

#### Backend ne démarre pas
```bash
# Vérifier Python
python --version

# Réinstaller les dépendances
pip uninstall -r requirements-simple.txt -y
pip install -r requirements-simple.txt
```

#### Desktop App ne charge pas
```bash
# Vérifier Node.js
node --version

# Nettoyer et réinstaller
rm -rf node_modules package-lock.json
npm install
```

#### Port déjà utilisé
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

## 📊 Monitoring

### Logs Backend
```bash
# Logs en temps réel
tail -f backend/logs/app.log

# Logs d'erreur
tail -f backend/logs/error.log
```

### Logs Desktop
```bash
# Console Electron
# Voir la console dans l'application (F12)
```

## 🚀 Déploiement

### Docker (Recommandé)
```bash
docker-compose up -d
```

### Production
```bash
# Backend
cd backend
pip install -r requirements-simple.txt
python main_simple.py

# Desktop
cd desktop
npm run build
npm run electron:build
```

## 📞 Support

- **Documentation API**: http://localhost:8000/docs
- **Issues**: GitHub Issues
- **Email**: support@proctoflex.ai

## 📄 Licence

MIT License - Voir LICENSE pour plus de détails.

---

**ProctoFlex AI** - Surveillance intelligente pour examens en ligne 🎓
