# ProctoFlex AI - Backend Simplifié

Backend FastAPI optimisé pour Windows avec configuration simplifiée.

## 🚀 Démarrage Rapide

### 1. Installation des dépendances
```bash
python install_simple.py
```

### 2. Démarrage du serveur
```bash
# Option 1: Script simplifié (recommandé)
python start_simple.py

# Option 2: Script original
python start.py
```

### 3. Accès à l'application
- **Application principale**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs
- **Documentation alternative**: http://localhost:8000/redoc

## 📁 Structure Simplifiée

```
backend/
├── app/                    # Code de l'application
├── requirements.txt        # Dépendances optimisées
├── install_simple.py      # Installation simplifiée
├── start_simple.py        # Démarrage simplifié
├── start.py              # Démarrage original
└── main_simple.py        # Point d'entrée principal
```

## 🔧 Configuration

Le serveur utilise maintenant une configuration directe :
- **Host**: localhost
- **Port**: 8000
- **Debug**: true
- **Base de données**: SQLite (proctoflex.db)

## 📦 Dépendances Incluses

- **FastAPI** + **Uvicorn** - Framework web
- **SQLAlchemy** - ORM pour base de données
- **OpenCV** + **NumPy** + **Pillow** - IA/Computer Vision
- **Python-Jose** + **Passlib** - Sécurité
- **Pytest** - Tests

## 🛠️ Dépannage

### Problème d'encodage .env
Si vous rencontrez des erreurs d'encodage, utilisez :
```bash
python start_simple.py
```

### Problème de dépendances
Réinstallez les dépendances :
```bash
python install_simple.py
```

### Problème de port
Si le port 8000 est occupé, modifiez la ligne dans `start_simple.py` :
```python
port = 8001  # ou un autre port disponible
```

## 🎯 Avantages de cette Version

✅ **Configuration simplifiée** - Pas de fichier .env complexe
✅ **Dépendances optimisées** - Seulement les packages essentiels
✅ **Compatibilité Windows** - Testé et optimisé
✅ **Démarrage rapide** - Scripts simplifiés
✅ **Moins d'erreurs** - Configuration directe

## 📞 Support

Pour toute question :
1. Vérifiez que Python 3.8+ est installé
2. Exécutez `python install_simple.py`
3. Utilisez `python start_simple.py`
4. Accédez à http://localhost:8000
