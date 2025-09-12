#!/usr/bin/env python3
"""
Script de test pour la création d'examens avec étudiants
"""

import requests
import json

API_BASE = "http://localhost:8000/api/v1"

def test_exam_creation():
    """Test de création d'examen avec sélection d'étudiants"""
    print("🧪 Test de création d'examen avec étudiants")
    print("=" * 50)
    
    # Test 1: Créer un examen avec des étudiants
    print("\n1. Création d'un examen avec étudiants...")
    try:
        exam_data = {
            "title": "Examen de Test avec Étudiants",
            "description": "Examen pour tester la sélection d'étudiants",
            "duration_minutes": 90,
            "status": "draft",
            "instructions": "Instructions pour l'examen",
            "selected_students": [2, 3],  # IDs des étudiants
            "instructor_id": 1
        }
        
        response = requests.post(f"{API_BASE}/exams", json=exam_data)
        
        if response.status_code == 200:
            exam = response.json()
            print(f"✅ Examen créé avec succès:")
            print(f"   - ID: {exam['id']}")
            print(f"   - Titre: {exam['title']}")
            print(f"   - Étudiants sélectionnés: {exam.get('selected_students', [])}")
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 2: Vérifier les examens d'un étudiant
    print("\n2. Vérification des examens de l'étudiant ID 2...")
    try:
        response = requests.get(f"{API_BASE}/students/2/exams")
        
        if response.status_code == 200:
            exams = response.json()
            print(f"✅ {len(exams)} examens trouvés pour l'étudiant:")
            for exam in exams:
                print(f"   - {exam['title']} (Statut: {exam['exam_status']})")
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Tests terminés!")

if __name__ == "__main__":
    test_exam_creation()