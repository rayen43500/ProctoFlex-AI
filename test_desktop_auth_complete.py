#!/usr/bin/env python3
"""
Script de test complet pour l'authentification desktop
"""

import requests
import json

API_BASE = "http://localhost:8000/api/v1"

def test_desktop_auth_flow():
    """Test complet du flux d'authentification desktop"""
    print("🖥️ Test complet de l'authentification desktop")
    print("=" * 60)
    
    # Test 1: Créer un utilisateur pour l'application desktop
    print("\n1. Création d'un utilisateur pour l'application desktop...")
    try:
        register_data = {
            "email": "desktop_user@example.com",
            "username": "desktop_user",
            "full_name": "Desktop User",
            "password": "desktop123",
            "role": "student",
            "face_image_base64": "fake_face_data_for_desktop_testing"
        }
        
        response = requests.post(f"{API_BASE}/auth/register-with-face", json=register_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Utilisateur desktop créé:")
            print(f"   - Username: {data.get('user', {}).get('username', 'N/A')}")
            print(f"   - Email: {data.get('user', {}).get('email', 'N/A')}")
            print(f"   - Rôle: {data.get('user', {}).get('role', 'N/A')}")
            print(f"   - ID: {data.get('user', {}).get('id', 'N/A')}")
        else:
            print(f"❌ Erreur création utilisateur: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return
    
    # Test 2: Login avec identifiants classiques
    print("\n2. Test de login avec identifiants classiques...")
    try:
        login_data = {
            "username": "desktop_user@example.com",
            "password": "desktop123"
        }
        
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login classique réussi:")
            print(f"   - Token: {data.get('access_token', 'N/A')[:20]}...")
            print(f"   - Utilisateur: {data.get('user', {}).get('username', 'N/A')}")
            print(f"   - Rôle: {data.get('user', {}).get('role', 'N/A')}")
        else:
            print(f"❌ Erreur login classique: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 3: Login avec visage
    print("\n3. Test de login avec visage...")
    try:
        face_data = {
            "face_image_base64": "fake_face_data_for_desktop_testing"
        }
        
        response = requests.post(f"{API_BASE}/auth/login-with-face", json=face_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login avec visage réussi:")
            print(f"   - Token: {data.get('access_token', 'N/A')[:20]}...")
            print(f"   - Utilisateur: {data.get('user', {}).get('username', 'N/A')}")
            print(f"   - Rôle: {data.get('user', {}).get('role', 'N/A')}")
        else:
            print(f"❌ Erreur login visage: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 4: Vérifier que l'utilisateur peut récupérer ses examens
    print("\n4. Test de récupération des examens de l'utilisateur...")
    try:
        # D'abord, créer un examen et l'assigner à cet utilisateur
        exam_data = {
            "title": "Examen Desktop Test",
            "description": "Examen pour tester l'application desktop",
            "duration_minutes": 60,
            "status": "draft",
            "instructions": "Instructions pour l'examen desktop",
            "selected_students": [data.get('user', {}).get('id', 0)],
            "instructor_id": 1
        }
        
        response = requests.post(f"{API_BASE}/exams", json=exam_data)
        
        if response.status_code == 200:
            exam = response.json()
            print(f"✅ Examen créé et assigné:")
            print(f"   - Titre: {exam.get('title', 'N/A')}")
            print(f"   - ID: {exam.get('id', 'N/A')}")
            
            # Maintenant, récupérer les examens de l'utilisateur
            user_id = data.get('user', {}).get('id', 0)
            response = requests.get(f"{API_BASE}/students/{user_id}/exams")
            
            if response.status_code == 200:
                exams = response.json()
                print(f"✅ {len(exams)} examens trouvés pour l'utilisateur:")
                for exam in exams:
                    print(f"   - {exam.get('title', 'N/A')} (Statut: {exam.get('exam_status', 'N/A')})")
            else:
                print(f"❌ Erreur récupération examens: {response.status_code}")
        else:
            print(f"❌ Erreur création examen: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Tests d'authentification desktop terminés!")
    print("\n📋 Instructions pour l'application desktop:")
    print("   - Email: desktop_user@example.com")
    print("   - Mot de passe: desktop123")
    print("   - Ou utilisez la reconnaissance faciale")

if __name__ == "__main__":
    test_desktop_auth_flow()
