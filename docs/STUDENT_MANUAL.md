# Manuel Étudiant - ProctoFlex AI

**Université de Monastir - ESPRIM**  
**École Supérieure Privée d'Ingénieurs de Monastir**

---

## Table des Matières

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Première Utilisation](#première-utilisation)
4. [Passage d'un Examen](#passage-dun-examen)
5. [Fonctionnalités de Surveillance](#fonctionnalités-de-surveillance)
6. [Résolution de Problèmes](#résolution-de-problèmes)
7. [FAQ](#faq)

---

## Introduction

ProctoFlex AI est une application de surveillance pour les examens en ligne. Elle garantit l'intégrité académique tout en vous permettant d'utiliser les logiciels nécessaires à votre examen.

### Pourquoi ProctoFlex AI ?

- **Flexibilité** : Utilisez vos logiciels habituels (IDE, Excel, etc.)
- **Sécurité** : Surveillance intelligente sans restriction excessive
- **Transparence** : Vous savez exactement ce qui est surveillé
- **Conformité** : Respect des réglementations RGPD

### Ce qui est Surveillé

- **Votre visage** : Pour vérifier votre identité
- **Votre regard** : Pour s'assurer que vous regardez l'écran
- **L'audio** : Pour détecter les conversations
- **Les applications** : Pour contrôler les logiciels utilisés
- **L'écran** : Pour surveiller les activités

---

## Installation

### Prérequis

- **Windows** : Windows 10 ou 11
- **macOS** : macOS 10.15 ou plus récent
- **Linux** : Ubuntu 18.04+ ou distribution compatible
- **Webcam** : Caméra fonctionnelle
- **Microphone** : Micro fonctionnel
- **Connexion Internet** : Stable (minimum 10 Mbps)

### Téléchargement

1. Rendez-vous sur le site de votre université
2. Connectez-vous avec vos identifiants étudiants
3. Téléchargez l'application pour votre système

### Installation Windows

1. **Exécuter l'installateur**
   - Double-cliquez sur `ProctoFlex-AI-Setup.exe`
   - Suivez les instructions d'installation

2. **Permissions requises**
   - Accès à la webcam
   - Accès au microphone
   - Accès aux applications
   - Accès au réseau

3. **Vérification**
   - L'application apparaît dans le menu Démarrer
   - L'icône est visible dans la barre des tâches

### Installation macOS

1. **Ouvrir le fichier DMG**
   - Double-cliquez sur `ProctoFlex-AI.dmg`
   - Glissez l'application vers le dossier Applications

2. **Autoriser l'application**
   - Ouvrez les Préférences Système
   - Allez dans Sécurité et confidentialité
   - Autorisez ProctoFlex AI

3. **Premier lancement**
   - L'application peut demander des permissions
   - Acceptez les permissions requises

### Installation Linux

1. **Rendre exécutable**
   ```bash
   chmod +x ProctoFlex-AI.AppImage
   ```

2. **Lancer l'application**
   ```bash
   ./ProctoFlex-AI.AppImage
   ```

3. **Créer un raccourci** (optionnel)
   ```bash
   sudo cp ProctoFlex-AI.AppImage /usr/local/bin/
   ```

---

## Première Utilisation

### Configuration Initiale

#### 1. Lancement de l'Application

1. Ouvrez ProctoFlex AI
2. Acceptez les conditions d'utilisation
3. Configurez vos préférences

#### 2. Test des Périphériques

L'application va tester :
- **Webcam** : Vérification de la qualité d'image
- **Microphone** : Test de l'audio
- **Connexion** : Test de la connectivité réseau

#### 3. Vérification d'Identité

1. **Photo d'identité**
   - Prenez une photo de votre pièce d'identité
   - Assurez-vous que le texte est lisible
   - La photo sera utilisée pour la vérification

2. **Photo de profil**
   - Prenez une photo de votre visage
   - Regardez directement la caméra
   - Assurez-vous d'avoir un bon éclairage

3. **Validation**
   - L'application compare les deux photos
   - Si la vérification échoue, recommencez

### Paramètres Recommandés

#### Environnement de Travail

- **Éclairage** : Lumière naturelle ou éclairage uniforme
- **Arrière-plan** : Mur uni, éviter les motifs
- **Position** : Assis face à la caméra
- **Distance** : 50-80 cm de l'écran

#### Périphériques

- **Webcam** : Positionnée au-dessus de l'écran
- **Microphone** : Éviter les bruits de fond
- **Écran** : Résolution minimale 1280x720

---

## Passage d'un Examen

### Avant l'Examen

#### 1. Préparation

- **Vérifiez votre connexion** : Testez votre internet
- **Fermez les applications** : Fermez les logiciels non nécessaires
- **Préparez votre espace** : Organisez votre bureau
- **Testez l'application** : Vérifiez que tout fonctionne

#### 2. Connexion

1. **Ouvrez ProctoFlex AI**
2. **Connectez-vous** avec vos identifiants
3. **Sélectionnez l'examen** dans la liste
4. **Lisez les instructions** attentivement

#### 3. Vérification Finale

- **Test de la webcam** : Vérifiez que vous êtes visible
- **Test du microphone** : Parlez pour tester l'audio
- **Test de l'écran** : Vérifiez l'affichage
- **Applications autorisées** : Vérifiez la liste

### Pendant l'Examen

#### 1. Démarrage

1. **Cliquez sur "Commencer l'examen"**
2. **Attendez la vérification d'identité**
3. **Confirmez que vous êtes prêt**

#### 2. Interface d'Examen

```
┌─────────────────────────────────────┐
│ ProctoFlex AI - Examen en Cours    │
├─────────────────────────────────────┤
│ Temps restant: 01:45:30            │
│ Statut: ✅ Surveillance active      │
│ Violations: 0                       │
├─────────────────────────────────────┤
│ [Soumettre l'examen]               │
└─────────────────────────────────────┘
```

#### 3. Règles à Respecter

##### ✅ Autorisé
- Utiliser les applications listées
- Consulter les sites web autorisés
- Prendre des notes sur papier
- Boire de l'eau

##### ❌ Interdit
- Ouvrir des applications non autorisées
- Consulter des sites non autorisés
- Parler ou communiquer
- Utiliser un téléphone
- Quitter la pièce

#### 4. Surveillance en Temps Réel

L'application surveille :
- **Votre visage** : Pour s'assurer de votre présence
- **Votre regard** : Pour vérifier votre attention
- **L'audio** : Pour détecter les conversations
- **Les applications** : Pour contrôler l'usage

### Alertes et Avertissements

#### Types d'Alertes

| Type | Description | Action Requise |
|------|-------------|----------------|
| ⚠️ Visage non visible | Votre visage n'est pas détecté | Regardez la caméra |
| 👁️ Regard détourné | Vous ne regardez pas l'écran | Concentrez-vous sur l'écran |
| 🎤 Voix détectée | Parole détectée | Arrêtez de parler |
| 🚫 App interdite | Application non autorisée | Fermez l'application |
| 📱 Objet suspect | Téléphone ou tablette détecté | Retirez l'objet |

#### Gestion des Alertes

1. **Lisez le message** attentivement
2. **Suivez les instructions** données
3. **Corrigez le problème** rapidement
4. **Confirmez** que le problème est résolu

### Fin d'Examen

#### 1. Soumission

1. **Cliquez sur "Soumettre l'examen"**
2. **Confirmez** votre soumission
3. **Attendez** la confirmation

#### 2. Finalisation

- **Enregistrements** : Les données sont sauvegardées
- **Rapport** : Un résumé est généré
- **Déconnexion** : Vous pouvez fermer l'application

---

## Fonctionnalités de Surveillance

### Reconnaissance Faciale

#### Comment ça marche
- **Détection** : L'IA détecte votre visage
- **Vérification** : Compare avec votre photo d'identité
- **Suivi** : Suit votre visage pendant l'examen

#### Conseils
- Gardez votre visage visible
- Évitez les mouvements brusques
- Maintenez une bonne posture

### Analyse du Regard

#### Fonctionnement
- **Direction** : Détecte où vous regardez
- **Attention** : Mesure votre concentration
- **Détournement** : Alerte si vous regardez ailleurs

#### Bonnes Pratiques
- Regardez l'écran principalement
- Évitez de regarder votre téléphone
- Restez concentré sur l'examen

### Surveillance Audio

#### Détection
- **Voix** : Détecte la parole
- **Bruit** : Analyse l'environnement sonore
- **Conversations** : Identifie les discussions

#### Environnement Idéal
- Pièce calme et isolée
- Évitez les bruits de fond
- Ne parlez pas pendant l'examen

### Contrôle des Applications

#### Applications Autorisées
- **IDEs** : Visual Studio Code, IntelliJ, Eclipse
- **Navigateurs** : Chrome, Firefox, Edge
- **Outils** : Calculatrice, Bloc-notes
- **Logiciels** : Selon l'examen

#### Applications Interdites
- **Communication** : Discord, WhatsApp, Skype
- **Réseaux sociaux** : Facebook, Twitter, Instagram
- **Divertissement** : YouTube, Netflix, Jeux

### Surveillance d'Écran

#### Activités Surveillées
- **Changements de fenêtre** : Fréquence des basculements
- **Copier-coller** : Activité excessive
- **Partage d'écran** : Détection de partage
- **Applications** : Ouverture de logiciels

---

## Résolution de Problèmes

### Problèmes Courants

#### 1. Webcam ne fonctionne pas

**Symptômes** : Image noire, erreur de caméra

**Solutions** :
- Vérifiez que la webcam est connectée
- Fermez les autres applications utilisant la caméra
- Redémarrez l'application
- Vérifiez les permissions dans les paramètres

#### 2. Microphone non détecté

**Symptômes** : Pas de son, erreur de microphone

**Solutions** :
- Vérifiez que le microphone est connecté
- Testez le microphone dans d'autres applications
- Vérifiez les paramètres audio
- Redémarrez l'application

#### 3. Connexion instable

**Symptômes** : Déconnexions fréquentes, lenteur

**Solutions** :
- Vérifiez votre connexion internet
- Fermez les autres applications utilisant le réseau
- Redémarrez votre routeur
- Contactez le support technique

#### 4. Application lente

**Symptômes** : Ralentissements, interface qui se fige

**Solutions** :
- Fermez les autres applications
- Redémarrez l'ordinateur
- Vérifiez l'espace disque disponible
- Mettez à jour l'application

### Codes d'Erreur

| Code | Description | Solution |
|------|-------------|----------|
| E001 | Webcam non trouvée | Vérifiez la connexion |
| E002 | Microphone non trouvé | Vérifiez les paramètres audio |
| E003 | Connexion échouée | Vérifiez votre internet |
| E004 | Permission refusée | Accordez les permissions |
| E005 | Application non autorisée | Fermez l'application |

### Support Technique

#### Contact

- **Email** : support@esprim.tn
- **Téléphone** : +216 73 500 000
- **Chat** : Disponible sur le site web
- **Heures** : 8h-18h (Lun-Ven)

#### Informations à Fournir

- Votre numéro d'étudiant
- Description du problème
- Messages d'erreur
- Captures d'écran
- Version de l'application

---

## FAQ

### Questions Générales

#### Q: Puis-je utiliser mon téléphone pendant l'examen ?
**R:** Non, l'utilisation du téléphone est interdite pendant l'examen. L'application détectera votre téléphone et générera une alerte.

#### Q: Que se passe-t-il si j'ai un problème technique ?
**R:** Contactez immédiatement le support technique. Votre session sera mise en pause pendant la résolution du problème.

#### Q: Puis-je boire ou manger pendant l'examen ?
**R:** Oui, vous pouvez boire de l'eau. Évitez les aliments qui pourraient faire du bruit.

#### Q: Que se passe-t-il si je regarde ailleurs ?
**R:** L'application détectera que vous ne regardez pas l'écran et vous alertera. Regardez rapidement l'écran pour corriger.

### Questions Techniques

#### Q: L'application ralentit-elle mon ordinateur ?
**R:** L'application est optimisée pour un impact minimal sur les performances. Elle utilise environ 5-10% des ressources.

#### Q: Mes données sont-elles sécurisées ?
**R:** Oui, toutes vos données sont chiffrées et stockées de manière sécurisée conformément au RGPD.

#### Q: Puis-je désactiver la surveillance ?
**R:** Non, la surveillance est obligatoire pendant l'examen pour garantir l'intégrité académique.

#### Q: Que se passe-t-il si je ferme l'application ?
**R:** L'examen sera automatiquement soumis et votre session sera terminée.

### Questions sur les Données

#### Q: Que se passe-t-il avec mes données après l'examen ?
**R:** Vos données sont conservées selon les politiques de rétention (90 jours pour les données biométriques).

#### Q: Puis-je demander la suppression de mes données ?
**R:** Oui, vous avez le droit de demander la suppression de vos données personnelles.

#### Q: Qui a accès à mes données ?
**R:** Seuls les administrateurs autorisés et les instructeurs de votre examen ont accès à vos données.

---

## Conclusion

ProctoFlex AI est conçu pour garantir l'intégrité de vos examens tout en vous permettant de travailler dans un environnement familier. Si vous avez des questions ou des problèmes, n'hésitez pas à contacter le support technique.

**Bon examen !**

---

**ProctoFlex AI** - Surveillance intelligente pour l'éducation  
© 2025 Université de Monastir - ESPRIM
