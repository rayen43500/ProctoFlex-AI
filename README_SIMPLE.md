# ProctoFlex AI - Plateforme de Surveillance d'Examens

Plateforme complète de surveillance intelligente d'examens en ligne avec reconnaissance faciale.

## 🚀 Démarrage Rapide

### Option 1: Démarrage complet (Recommandé)
```bash
# Double-cliquez sur le fichier
start_all.bat
```
**Démarre automatiquement le backend ET l'application desktop**

### Option 2: Démarrage séparé
```bash
# Backend seulement
start_backend.bat

# Application desktop seulement
start_desktop.bat
```

### Option 3: Démarrage manuel
```bash
# Backend
cd backend
python start_simple.py

# Desktop (dans un autre terminal)
cd desktop
npm run dev
```

## 📋 Prérequis

- **Python 3.8+** (https://python.org/)
- **Node.js 16+** (https://nodejs.org/)
- **npm** (inclus avec Node.js)

## 🏗️ Architecture

```
nisrine twity/
├── backend/              # API FastAPI (Python)
│   ├── start_simple.py   # Démarrage backend
│   └── install_simple.py # Installation dépendances
├── desktop/              # Application Electron (React/TypeScript)
│   ├── start_fix.bat     # Démarrage desktop
│   └── package.json      # Dépendances Node.js
├── start_all.bat         # Démarrage complet
├── start_backend.bat     # Démarrage backend
└── start_desktop.bat     # Démarrage desktop
```

## 🎯 Fonctionnalités

### Backend (API)
- ✅ **Authentification JWT** - Connexion sécurisée
- ✅ **Reconnaissance faciale** - OpenCV + IA
- ✅ **Surveillance temps réel** - WebSockets
- ✅ **Base de données SQLite** - Stockage local
- ✅ **API REST** - Documentation automatique

### Application Desktop
- ✅ **Interface moderne** - React + Tailwind CSS
- ✅ **Vérification biométrique** - Caméra intégrée
- ✅ **Monitoring processus** - Détection de triche
- ✅ **Session d'examen** - Interface étudiant
- ✅ **Notifications temps réel** - Toast messages

## 🌐 Accès aux Applications

Une fois démarrées :
- **Backend API**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs
- **Application Desktop**: Se lance automatiquement

## 🛠️ Scripts Disponibles

### Scripts Principaux
- `start_all.bat` - Démarrage complet (backend + desktop)
- `start_backend.bat` - Backend seulement
- `start_desktop.bat` - Desktop seulement

### Scripts Spécialisés
- `backend/start_simple.py` - Backend optimisé
- `desktop/start_fix.bat` - Desktop avec corrections

## 🚨 Dépannage

### Erreur "Python not found"
```bash
# Installez Python depuis https://python.org/
```

### Erreur "Node.js not found"
```bash
# Installez Node.js depuis https://nodejs.org/
```

### Erreur "Package not found"
```bash
# Backend
cd backend
python install_simple.py

# Desktop
cd desktop
npm install
```

### Port 8000 déjà utilisé
```bash
# Arrêtez l'application qui utilise le port 8000
# Ou modifiez le port dans backend/start_simple.py
```

## 📞 Support

1. **Vérifiez les prérequis** - Python et Node.js installés
2. **Utilisez start_all.bat** - Démarrage automatique
3. **Consultez les logs** - Messages d'erreur dans les fenêtres
4. **Vérifiez les ports** - 8000 pour backend, 5173 pour desktop

## 🎯 Avantages

✅ **Démarrage simple** - Scripts automatisés  
✅ **Configuration optimisée** - Moins d'erreurs  
✅ **Documentation complète** - Guides étape par étape  
✅ **Compatibilité Windows** - Testé et optimisé  
✅ **Architecture moderne** - FastAPI + Electron + React  

## 🔧 Développement

Pour le développement :
```bash
# Backend en mode développement
cd backend
python start_simple.py

# Desktop en mode développement
cd desktop
npm run dev
```

---

**💡 Conseil :** Utilisez `start_all.bat` pour un démarrage sans problème !
