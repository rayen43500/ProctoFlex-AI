# ProctoFlex AI - Système de Surveillance d'Examens

## 🚀 Démarrage Rapide

### 1. Installer les dépendances

```bash
# Backend
cd backend
python install_simple.py

# Frontend  
cd frontend
npm install

# Desktop
cd desktop
npm install
```

### 2. Démarrer les services

**Option A : Script automatique**
```bash
start_all_services.bat
```

**Option B : Manuel**
```bash
# Backend (Terminal 1)
cd backend
python main_simple.py

# Frontend (Terminal 2)  
cd frontend
npm run dev

# Desktop (Terminal 3)
cd desktop
npm run dev
```

## 📍 URLs

- **Backend API** : http://localhost:8000
- **Frontend Admin** : http://localhost:3000
- **Desktop App** : Application Electron

## 🛠️ Scripts Utiles

- `start_all_services.bat` - Démarre tout
- `start_frontend.bat` - Frontend seulement
- `start_backend.bat` - Backend seulement

## 📁 Structure

```
├── backend/     # API FastAPI + AI
├── frontend/    # Interface Admin React
├── desktop/     # App Electron
└── docs/        # Documentation
```

## �️ Base de Données

Le projet utilise PostgreSQL par défaut (voir `docker-compose.yml`). Vous pouvez changer de SGBD via la variable `DATABASE_URL` (supportés: PostgreSQL, MySQL/MariaDB via `mysql+pymysql://`). SQLite n'est plus supporté.

Exemples :
```
DATABASE_URL=postgresql://user:pass@localhost:5432/proctoflex
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/proctoflex
```

Pour les tests, utilisez une base PostgreSQL dédiée via `DATABASE_TEST_URL`.

## 🤖 Modèle YOLO

La détection d'objets tente de charger `models/yolov5s.pt`.

Variables utiles dans `.env` :
```
AI_ENABLE_YOLO=true
YOLO_MODEL_PATH=models/yolov5s.pt
YOLO_AUTO_DOWNLOAD=true
```
Si le fichier est absent et `YOLO_AUTO_DOWNLOAD=true`, il sera téléchargé automatiquement depuis les releases officielles. Mettre `AI_ENABLE_YOLO=false` pour désactiver et n'utiliser que le fallback OpenCV.

## 🧪 Tests

Des tests basiques sont disponibles dans `backend/tests/`.

Exécution :
```bash
cd backend
pytest -q
```

## 📄 Documentation Technique

Voir :
- `docs/architecture.md` : Architecture détaillée
- `docs/api.md` : Spécification endpoints
- `backend/app/compliance/gdpr_service.py` : Implémentation RGPD

## ✅ Qualité & Roadmap

Améliorations futures :
- Ajout de tests pour endpoints critiques (auth, surveillance)
- Intégration CI (GitHub Actions) pour lint + tests
- Téléchargement optionnel modèles IA lourds (poids configurables)

## �🔧 Dépannage

**Erreur de dépendances** : Relancer `npm install` ou `python install_simple.py`

**Port occupé** : Vérifier qu'aucun autre service n'utilise les ports 8000/3000

**Cache Vite** : Supprimer `frontend/node_modules/.vite` et redémarrer

**YOLO non chargé** : Vérifier `models/yolov5s.pt`, variables `.env` ou désactiver `AI_ENABLE_YOLO`.

**Connexion DB** : Tester `psql` ou ajuster `DATABASE_URL`. Pour MySQL installer `pymysql` :
```bash
pip install pymysql
```



docker-compose -f docker-compose.dev.yml up -d


rayen985958@gmail.com