# ProctoFlex AI

Plateforme de surveillance flexible pour examens pratiques en ligne avec vérification d'identité et détection IA multimodale.

## 🎯 Objectif

Assurer une surveillance fiable et respectueuse des examens pratiques à distance, spécialement conçue pour les épreuves nécessitant des logiciels installés localement (IDE, AutoCAD, Excel, etc.).

## 🏗️ Architecture

Le projet est divisé en trois composants principaux :

- **Frontend Admin** (`/frontend`) - Interface web React.js pour les administrateurs
- **Backend** (`/backend`) - API FastAPI avec moteur IA et base PostgreSQL
- **Client Desktop** (`/desktop`) - Application Electron pour les étudiants

## 🚀 Installation et Démarrage

### Prérequis

- Python 3.9+
- Node.js 18+
- PostgreSQL 13+
- Docker (optionnel)

### Démarrage Rapide

1. **Cloner le projet**
```bash
git clone <repository-url>
cd proctoflex-ai
```

2. **Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

3. **Frontend Admin**
```bash
cd frontend
npm install
npm run dev
```

4. **Client Desktop**
```bash
cd desktop
npm install
npm run dev
```

## 📋 Fonctionnalités MVP

### Phase 1 (Semaines 1-3)
- [ ] Application desktop de base (Electron)
- [ ] Verrouillage sélectif des applications
- [ ] Authentification par reconnaissance faciale

### Phase 2 (Semaines 4-6)
- [ ] Dashboard administrateur
- [ ] Enregistrement multimédia (webcam, micro, écran)

### Phase 3 (Semaines 7-9)
- [ ] Moteur IA de détection
- [ ] Système d'alertes intelligent

### Phase 4 (Semaines 10-12)
- [ ] Tests utilisateurs
- [ ] Finalisation et documentation

## 🔒 Sécurité et RGPD

- Chiffrement TLS 1.3
- Données localisées en Europe
- Suppression automatique après 90 jours
- Consentement explicite requis

## 👥 Équipe

- **Encadrant** : Abdlekrim Mars
- **Développeurs** : Nesrine Touiti, Sarra Lahgui, Chaima Jbara
- **Institution** : ESPRIM - École Supérieure Privée d'Ingénieurs de Monastir

## 📅 Planning

- **Cadrage** : 22 juin 2024 ✅
- **Sprint 1** : Semaines 1-3
- **Sprint 2** : Semaines 4-6  
- **Sprint 3** : Semaines 7-9
- **Sprint 4** : Semaines 10-12
- **Livraison** : Août 2025

## 📚 Documentation

- [Manuel Administrateur](./docs/admin-manual.md)
- [Manuel Étudiant](./docs/student-manual.md)
- [API Documentation](./docs/api.md)
- [Architecture Technique](./docs/architecture.md)
