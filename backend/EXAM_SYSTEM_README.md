# Système de Gestion des Examens - ProctoFlex AI

## Vue d'ensemble

Le système de gestion des examens permet aux instructeurs et administrateurs de créer, modifier et gérer des examens avec support des fichiers PDF.

## Fonctionnalités

### ✅ Création d'examens
- Titre et description
- Durée en minutes
- Instructions détaillées
- Statut (Brouillon, Programmé, Actif, Terminé, Annulé)
- Upload de fichiers PDF
- Applications et domaines autorisés

### ✅ Gestion des examens
- Liste des examens avec filtres
- Modification des examens existants
- Suppression (soft delete)
- Téléchargement des fichiers PDF

### ✅ Sécurité
- Authentification requise
- Autorisation basée sur les rôles
- Validation des fichiers PDF
- Stockage sécurisé des fichiers

## Structure de la Base de Données

### Table `exams`
```sql
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
    allowed_apps TEXT,  -- JSON string
    allowed_domains TEXT,  -- JSON string
    pdf_path VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## API Endpoints

### Examens
- `POST /api/v1/exams` - Créer un examen
- `GET /api/v1/exams` - Liste des examens
- `GET /api/v1/exams/{id}` - Détails d'un examen
- `PUT /api/v1/exams/{id}` - Modifier un examen
- `DELETE /api/v1/exams/{id}` - Supprimer un examen

### Fichiers PDF
- `POST /api/v1/exams/{id}/pdf` - Upload d'un PDF
- `GET /api/v1/exams/{id}/pdf` - Télécharger un PDF

## Installation et Configuration

### 1. Prérequis
- Python 3.8+
- PostgreSQL
- FastAPI
- SQLAlchemy

### 2. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 3. Configuration de la base de données
```bash
# Créer la base de données
createdb proctoflex

# Exécuter les migrations
psql proctoflex < init.sql
psql proctoflex < migrations/add_exam_fields.sql
```

### 4. Configuration des variables d'environnement
```bash
# Copier le fichier d'exemple
cp env.example .env

# Modifier les variables dans .env
DATABASE_URL=postgresql://user:password@localhost/proctoflex
SECRET_KEY=your-secret-key
```

### 5. Démarrage du serveur
```bash
# Mode développement
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Mode production
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Utilisation

### 1. Création d'un examen via API

```bash
curl -X POST "http://localhost:8000/api/v1/exams" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Examen de Mathématiques",
    "description": "Examen final de mathématiques",
    "duration_minutes": 120,
    "instructions": "Calculatrice autorisée",
    "status": "draft"
  }'
```

### 2. Upload d'un fichier PDF

```bash
curl -X POST "http://localhost:8000/api/v1/exams/1/pdf" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "pdf_file=@exam.pdf"
```

### 3. Interface Web

L'interface web est disponible dans le dossier `frontend/` et permet :
- Création/modification d'examens via formulaire
- Upload de fichiers PDF par glisser-déposer
- Gestion des examens avec interface intuitive

## Tests

### Exécuter les tests
```bash
python test_exam_system.py
```

### Tests automatisés
```bash
pytest tests/test_exam_crud.py
pytest tests/test_exam_api.py
```

## Sécurité

### Authentification
- JWT tokens requis pour toutes les opérations
- Expiration automatique des tokens
- Refresh tokens pour la continuité de session

### Autorisation
- Instructeurs : peuvent créer/modifier leurs examens
- Administrateurs : accès complet à tous les examens
- Étudiants : accès en lecture seule

### Validation des fichiers
- Seuls les fichiers PDF sont acceptés
- Vérification de la taille des fichiers
- Noms de fichiers sécurisés (UUID)

## Stockage des fichiers

### Structure des dossiers
```
uploads/
└── exams/
    ├── 1_uuid1.pdf
    ├── 2_uuid2.pdf
    └── ...
```

### Sécurité
- Fichiers stockés en dehors du web root
- Noms de fichiers uniques (UUID)
- Validation du type MIME
- Suppression automatique des anciens fichiers

## Monitoring et Logs

### Logs d'audit
- Création/modification d'examens
- Upload/téléchargement de fichiers
- Tentatives d'accès non autorisées

### Métriques
- Nombre d'examens créés
- Taille des fichiers uploadés
- Temps de réponse des API

## Dépannage

### Problèmes courants

1. **Erreur de connexion à la base de données**
   - Vérifier la configuration DATABASE_URL
   - S'assurer que PostgreSQL est démarré

2. **Erreur d'upload de fichier**
   - Vérifier les permissions du dossier uploads/
   - Vérifier la taille du fichier

3. **Erreur d'authentification**
   - Vérifier la validité du token JWT
   - Vérifier la configuration SECRET_KEY

### Logs
```bash
# Logs du serveur
tail -f logs/app.log

# Logs de la base de données
tail -f /var/log/postgresql/postgresql.log
```

## Support

Pour toute question ou problème :
- Consulter les logs
- Vérifier la configuration
- Tester avec l'API directement
- Contacter l'équipe de développement

## Changelog

### Version 1.0.0
- ✅ Création du système de base
- ✅ API REST complète
- ✅ Interface web
- ✅ Support des fichiers PDF
- ✅ Sécurité et authentification
