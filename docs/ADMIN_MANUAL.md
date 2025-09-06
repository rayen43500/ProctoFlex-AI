# Manuel Administrateur - ProctoFlex AI

**Université de Monastir - ESPRIM**  
**École Supérieure Privée d'Ingénieurs de Monastir**

---

## Table des Matières

1. [Introduction](#introduction)
2. [Installation et Configuration](#installation-et-configuration)
3. [Interface Administrateur](#interface-administrateur)
4. [Gestion des Examens](#gestion-des-examens)
5. [Gestion des Étudiants](#gestion-des-étudiants)
6. [Surveillance et Alertes](#surveillance-et-alertes)
7. [Conformité RGPD](#conformité-rgpd)
8. [Maintenance et Support](#maintenance-et-support)

---

## Introduction

ProctoFlex AI est une plateforme de surveillance flexible pour examens pratiques en ligne avec vérification d'identité et détection IA multimodale. Ce manuel guide les administrateurs dans l'utilisation complète du système.

### Fonctionnalités Principales

- **Surveillance IA Temps Réel** : Reconnaissance faciale, analyse du regard, détection audio
- **Verrouillage Sélectif** : Contrôle des applications autorisées
- **Vérification d'Identité** : Authentification biométrique
- **Dashboard Administrateur** : Interface de gestion complète
- **Conformité RGPD** : Gestion des données personnelles

---

## Installation et Configuration

### Prérequis Système

- **OS** : Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **RAM** : 8 GB minimum, 16 GB recommandé
- **Stockage** : 10 GB d'espace libre
- **Réseau** : Connexion stable (100 Mbps recommandé)

### Installation

#### 1. Installation Automatique

```bash
# Télécharger et exécuter le script d'installation
curl -sSL https://install.proctoflex.ai | bash
```

#### 2. Installation Manuelle

1. **Télécharger les packages**
   - Windows : `ProctoFlex-AI-Setup.exe`
   - macOS : `ProctoFlex-AI.dmg`
   - Linux : `ProctoFlex-AI.AppImage`

2. **Installer l'application**
   - Suivre les instructions d'installation
   - Configurer les permissions requises

3. **Configuration initiale**
   ```bash
   # Lancer la configuration
   proctoflex-admin --setup
   ```

### Configuration Initiale

#### 1. Base de Données

```sql
-- Créer la base de données
CREATE DATABASE proctoflex;
CREATE USER proctoflex_admin WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE proctoflex TO proctoflex_admin;
```

#### 2. Variables d'Environnement

```bash
# Fichier .env
DATABASE_URL=postgresql://proctoflex_admin:secure_password@localhost:5432/proctoflex
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
```

#### 3. Services

```bash
# Démarrer les services
docker-compose up -d
```

---

## Interface Administrateur

### Accès au Dashboard

1. Ouvrir le navigateur
2. Naviguer vers `https://admin.proctoflex.ai`
3. Se connecter avec les identifiants administrateur

### Navigation Principale

#### Vue d'Ensemble
- **Statistiques en Temps Réel** : Examens actifs, sessions, alertes
- **Graphiques de Performance** : Tendances, métriques
- **Alertes Critiques** : Notifications importantes

#### Gestion des Examens
- **Création d'Examens** : Configuration complète
- **Planification** : Dates, heures, durées
- **Surveillance** : Sessions en cours

#### Gestion des Étudiants
- **Inscription** : Ajout d'étudiants
- **Groupes** : Organisation par classes
- **Permissions** : Accès aux examens

#### Surveillance
- **Alertes Temps Réel** : Incidents détectés
- **Sessions Actives** : Surveillance en direct
- **Rapports** : Analyses détaillées

---

## Gestion des Examens

### Création d'un Examen

#### 1. Informations de Base

```
Titre : Examen de Programmation
Description : Examen pratique de développement
Durée : 120 minutes
Type : Pratique
```

#### 2. Configuration de Surveillance

```json
{
  "video_surveillance": true,
  "audio_surveillance": true,
  "screen_recording": true,
  "face_detection": true,
  "gaze_tracking": true,
  "voice_detection": true
}
```

#### 3. Applications Autorisées

```json
{
  "allowed_apps": [
    "Visual Studio Code",
    "IntelliJ IDEA",
    "Eclipse",
    "Chrome",
    "Firefox"
  ],
  "blocked_apps": [
    "Discord",
    "Telegram",
    "WhatsApp",
    "Skype"
  ]
}
```

#### 4. Domaines Web Autorisés

```json
{
  "allowed_domains": [
    "docs.python.org",
    "stackoverflow.com",
    "github.com"
  ],
  "blocked_domains": [
    "facebook.com",
    "twitter.com",
    "youtube.com"
  ]
}
```

### Planification

#### Calendrier des Examens

- **Vue Mensuelle** : Tous les examens du mois
- **Vue Hebdomadaire** : Planning détaillé
- **Vue Quotidienne** : Examens du jour

#### Gestion des Conflits

- **Détection Automatique** : Conflits de planning
- **Résolution** : Suggestions de créneaux
- **Notifications** : Alertes aux instructeurs

### Surveillance en Temps Réel

#### Dashboard de Session

```
Session ID: SESS_2025_001
Étudiant: Ahmed Ben Ali
Examen: Programmation Avancée
Durée: 45/120 minutes
Violations: 2
Statut: Actif
```

#### Types d'Alertes

| Type | Niveau | Description |
|------|--------|-------------|
| Visage Non Visible | Critique | Aucun visage détecté |
| Regard Détourné | Moyen | Regard hors écran > 10s |
| Voix Détectée | Élevé | Parole pendant l'examen |
| App Non Autorisée | Critique | Application interdite ouverte |
| Copier-Coller | Moyen | Activité excessive |

---

## Gestion des Étudiants

### Inscription des Étudiants

#### 1. Import en Masse

```csv
student_id,first_name,last_name,email,class,group
2025001,Ahmed,Ben Ali,ahmed.benali@student.esprim.tn,DSIA2A,G1
2025002,Fatma,Ben Salem,fatma.bensalem@student.esprim.tn,DSIA2A,G1
2025003,Mohamed,Ben Ammar,mohamed.benammar@student.esprim.tn,DSIA2A,G2
```

#### 2. Inscription Individuelle

```json
{
  "student_id": "2025001",
  "first_name": "Ahmed",
  "last_name": "Ben Ali",
  "email": "ahmed.benali@student.esprim.tn",
  "class": "DSIA2A",
  "group": "G1",
  "phone": "+216 12 345 678"
}
```

### Gestion des Groupes

#### Création de Groupes

```
Nom: DSIA2A_G1
Description: Groupe 1 - Data Science 2ème année
Étudiants: 25
Instructeur: Dr. Mars
```

#### Attribution d'Examens

- **Par Groupe** : Tous les étudiants du groupe
- **Par Individu** : Étudiants sélectionnés
- **Par Critères** : Filtres personnalisés

### Permissions et Accès

#### Niveaux d'Accès

1. **Étudiant** : Participation aux examens
2. **Instructeur** : Gestion des examens assignés
3. **Administrateur** : Accès complet au système
4. **Super Admin** : Configuration système

#### Gestion des Rôles

```json
{
  "role": "instructor",
  "permissions": [
    "create_exam",
    "view_students",
    "monitor_sessions",
    "generate_reports"
  ],
  "restrictions": [
    "cannot_delete_students",
    "cannot_modify_system_settings"
  ]
}
```

---

## Surveillance et Alertes

### Système d'Alertes

#### Configuration des Seuils

```json
{
  "face_detection": {
    "enabled": true,
    "threshold": 0.7,
    "cooldown": 5
  },
  "gaze_tracking": {
    "enabled": true,
    "away_threshold": 10,
    "sensitivity": 0.8
  },
  "voice_detection": {
    "enabled": true,
    "threshold": 0.5,
    "duration_threshold": 3
  }
}
```

#### Types de Surveillance

##### 1. Surveillance Vidéo
- **Détection Faciale** : Présence et qualité du visage
- **Reconnaissance** : Vérification d'identité
- **Analyse du Regard** : Direction et attention
- **Détection d'Objets** : Téléphones, tablettes

##### 2. Surveillance Audio
- **Détection de Voix** : Parole pendant l'examen
- **Analyse du Bruit** : Environnement sonore
- **Reconnaissance Vocale** : Identification du locuteur

##### 3. Surveillance d'Écran
- **Applications Actives** : Contrôle des logiciels
- **Changements de Fenêtre** : Fréquence des basculements
- **Copier-Coller** : Activité de clavier
- **Partage d'Écran** : Détection de partage

### Gestion des Incidents

#### Workflow de Traitement

1. **Détection** : Alerte générée automatiquement
2. **Classification** : Niveau de gravité assigné
3. **Notification** : Alertes aux administrateurs
4. **Intervention** : Actions correctives
5. **Documentation** : Enregistrement de l'incident

#### Actions Disponibles

- **Avertissement** : Notification à l'étudiant
- **Pause** : Suspension temporaire
- **Terminaison** : Arrêt de la session
- **Rapport** : Documentation de l'incident

### Rapports et Analyses

#### Rapports Automatiques

- **Rapport de Session** : Résumé de chaque examen
- **Rapport d'Incidents** : Détail des violations
- **Rapport de Performance** : Métriques système
- **Rapport RGPD** : Conformité des données

#### Exports Disponibles

- **PDF** : Rapports formatés
- **CSV** : Données tabulaires
- **JSON** : Données structurées
- **Excel** : Feuilles de calcul

---

## Conformité RGPD

### Gestion des Consentements

#### Enregistrement des Consentements

```json
{
  "student_id": "2025001",
  "consent_date": "2025-01-15T10:30:00Z",
  "data_categories": [
    "identification",
    "biometric",
    "behavioral"
  ],
  "purposes": [
    "identity_verification",
    "exam_surveillance",
    "fraud_detection"
  ],
  "legal_basis": "consent",
  "withdrawal_date": null
}
```

#### Politiques de Rétention

| Type de Données | Durée de Conservation | Action |
|------------------|----------------------|--------|
| Identification | 3 ans | Suppression automatique |
| Biométriques | 90 jours | Suppression automatique |
| Comportementales | 90 jours | Suppression automatique |
| Techniques | 1 an | Suppression automatique |
| Académiques | 5 ans | Archivage |

### Droits des Personnes

#### Droit d'Accès

```json
{
  "request_type": "access",
  "student_id": "2025001",
  "data_categories": ["all"],
  "format": "json",
  "delivery_method": "email"
}
```

#### Droit à l'Effacement

```json
{
  "request_type": "erasure",
  "student_id": "2025001",
  "data_categories": ["biometric", "behavioral"],
  "reason": "withdrawal_of_consent"
}
```

### Audit et Traçabilité

#### Journal d'Audit

```
2025-01-15 10:30:00 | CONSENT_RECORDED | 2025001 | Consentement enregistré
2025-01-15 11:00:00 | DATA_PROCESSING | 2025001 | Traitement biométrique
2025-01-15 11:30:00 | ALERT_GENERATED | 2025001 | Alerte: regard détourné
```

#### Mesures de Sécurité

- **Chiffrement** : AES-256 pour les données au repos
- **Transit** : TLS 1.3 pour les communications
- **Accès** : Contrôle d'accès basé sur les rôles
- **Audit** : Journalisation complète des accès

---

## Maintenance et Support

### Surveillance Système

#### Métriques de Performance

```json
{
  "cpu_usage": 45.2,
  "memory_usage": 67.8,
  "disk_usage": 23.1,
  "network_latency": 12.5,
  "active_sessions": 15,
  "alerts_per_minute": 3.2
}
```

#### Alertes Système

- **CPU > 80%** : Charge processeur élevée
- **RAM > 90%** : Mémoire insuffisante
- **Disque > 85%** : Espace de stockage faible
- **Latence > 100ms** : Ralentissement réseau

### Sauvegarde et Récupération

#### Stratégie de Sauvegarde

```bash
# Sauvegarde quotidienne
0 2 * * * /usr/local/bin/proctoflex-backup daily

# Sauvegarde hebdomadaire
0 3 * * 0 /usr/local/bin/proctoflex-backup weekly

# Sauvegarde mensuelle
0 4 1 * * /usr/local/bin/proctoflex-backup monthly
```

#### Récupération d'Urgence

1. **Arrêt des Services** : Arrêter tous les services
2. **Restauration** : Restaurer depuis la sauvegarde
3. **Vérification** : Tester le fonctionnement
4. **Redémarrage** : Relancer les services

### Mise à Jour

#### Processus de Mise à Jour

1. **Sauvegarde** : Créer une sauvegarde complète
2. **Téléchargement** : Récupérer la nouvelle version
3. **Installation** : Installer la mise à jour
4. **Migration** : Migrer les données si nécessaire
5. **Test** : Vérifier le fonctionnement
6. **Déploiement** : Mettre en production

#### Rollback

```bash
# Retour à la version précédente
proctoflex-admin --rollback --version=1.2.3
```

### Support Technique

#### Niveaux de Support

1. **Niveau 1** : Support utilisateur (24h)
2. **Niveau 2** : Support technique (12h)
3. **Niveau 3** : Support développeur (4h)

#### Contacts

- **Email** : support@esprim.tn
- **Téléphone** : +216 73 500 000
- **Site Web** : https://support.proctoflex.ai
- **Documentation** : https://docs.proctoflex.ai

#### Escalade

```
Incident Critique → Niveau 3 (1h)
Incident Majeur → Niveau 2 (4h)
Incident Mineur → Niveau 1 (24h)
```

---

## Conclusion

Ce manuel couvre l'utilisation complète de ProctoFlex AI pour les administrateurs. Pour toute question ou assistance supplémentaire, contactez l'équipe de support.

**ProctoFlex AI** - Surveillance intelligente pour l'éducation  
© 2025 Université de Monastir - ESPRIM
