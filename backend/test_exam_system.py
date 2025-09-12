#!/usr/bin/env python3
"""
Script de test pour le système de gestion des examens
"""

import requests
import json
import os
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER = {
    "email": "test@instructor.com",
    "username": "test_instructor",
    "full_name": "Test Instructor",
    "password": "test123",
    "role": "instructor"
}

def test_exam_system():
    """Test complet du système de gestion des examens"""
    
    print("🧪 Test du système de gestion des examens")
    print("=" * 50)
    
    # 1. Créer un utilisateur instructeur
    print("\n1. Création d'un utilisateur instructeur...")
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
        if response.status_code == 201:
            print("✅ Utilisateur créé avec succès")
            user_data = response.json()
            token = user_data.get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"❌ Erreur création utilisateur: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    # 2. Créer un examen
    print("\n2. Création d'un examen...")
    exam_data = {
        "title": "Examen de Test",
        "description": "Description de l'examen de test",
        "duration_minutes": 60,
        "instructions": "Instructions pour l'examen",
        "status": "draft"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/exams", json=exam_data, headers=headers)
        if response.status_code == 201:
            print("✅ Examen créé avec succès")
            exam = response.json()
            exam_id = exam["id"]
            print(f"   ID: {exam_id}")
            print(f"   Titre: {exam['title']}")
            print(f"   Statut: {exam['status']}")
        else:
            print(f"❌ Erreur création examen: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    # 3. Récupérer la liste des examens
    print("\n3. Récupération de la liste des examens...")
    try:
        response = requests.get(f"{BASE_URL}/exams", headers=headers)
        if response.status_code == 200:
            data = response.json()
            exams = data["exams"]
            print(f"✅ {len(exams)} examen(s) trouvé(s)")
            for exam in exams:
                print(f"   - {exam['title']} (ID: {exam['id']}, Statut: {exam['status']})")
        else:
            print(f"❌ Erreur récupération: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # 4. Récupérer un examen spécifique
    print(f"\n4. Récupération de l'examen {exam_id}...")
    try:
        response = requests.get(f"{BASE_URL}/exams/{exam_id}", headers=headers)
        if response.status_code == 200:
            exam = response.json()
            print("✅ Examen récupéré avec succès")
            print(f"   Titre: {exam['title']}")
            print(f"   Description: {exam['description']}")
            print(f"   Durée: {exam['duration_minutes']} minutes")
            print(f"   Instructions: {exam['instructions']}")
        else:
            print(f"❌ Erreur récupération: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # 5. Mettre à jour l'examen
    print(f"\n5. Mise à jour de l'examen {exam_id}...")
    update_data = {
        "title": "Examen de Test Modifié",
        "status": "scheduled",
        "instructions": "Nouvelles instructions pour l'examen"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/exams/{exam_id}", json=update_data, headers=headers)
        if response.status_code == 200:
            exam = response.json()
            print("✅ Examen mis à jour avec succès")
            print(f"   Nouveau titre: {exam['title']}")
            print(f"   Nouveau statut: {exam['status']}")
        else:
            print(f"❌ Erreur mise à jour: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # 6. Test de téléchargement de PDF (simulation)
    print(f"\n6. Test de téléchargement de PDF...")
    try:
        response = requests.get(f"{BASE_URL}/exams/{exam_id}/pdf", headers=headers)
        if response.status_code == 404:
            print("✅ Endpoint PDF fonctionne (aucun fichier uploadé)")
        else:
            print(f"❌ Erreur inattendue: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # 7. Suppression de l'examen
    print(f"\n7. Suppression de l'examen {exam_id}...")
    try:
        response = requests.delete(f"{BASE_URL}/exams/{exam_id}", headers=headers)
        if response.status_code == 200:
            print("✅ Examen supprimé avec succès")
        else:
            print(f"❌ Erreur suppression: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test terminé!")

if __name__ == "__main__":
    test_exam_system()
