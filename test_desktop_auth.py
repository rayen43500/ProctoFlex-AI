#!/usr/bin/env python3
"""
Test d'authentification pour l'application desktop Electron
"""

import requests
import json

API_BASE = "http://localhost:8000/api/v1"

def test_login():
    """Test de connexion avec email et mot de passe"""
    print("🔐 Test d'authentification pour l'application desktop")
    print("=" * 50)
    
    # Test avec l'utilisateur étudiant
    login_data = {
        "username": "student@test.com",  # Le backend attend "username" mais on utilise l'email
        "password": "student123"
    }
    
    try:
        print(f"📧 Tentative de connexion avec: {login_data['username']}")
        
        response = requests.post(
            f"{API_BASE}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Connexion réussie!")
            print(f"   Token: {data.get('access_token', 'N/A')[:20]}...")
            print(f"   Utilisateur: {data.get('username', 'N/A')}")
            print(f"   Rôle: {data.get('role', 'N/A')}")
            
            # Test de récupération du profil utilisateur
            token = data.get('access_token')
            if token:
                print("\n👤 Test de récupération du profil utilisateur...")
                profile_response = requests.get(
                    f"{API_BASE}/auth/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print("✅ Profil récupéré avec succès!")
                    print(f"   ID: {profile_data.get('id', 'N/A')}")
                    print(f"   Email: {profile_data.get('email', 'N/A')}")
                    print(f"   Nom: {profile_data.get('full_name', 'N/A')}")
                    print(f"   Rôle: {profile_data.get('role', 'N/A')}")
                else:
                    print(f"❌ Erreur lors de la récupération du profil: {profile_response.status_code}")
                    print(f"   Réponse: {profile_response.text}")
            
            return True
            
        else:
            print(f"❌ Échec de la connexion: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("   Vérifiez que le serveur backend est démarré sur http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def test_student_exams():
    """Test de récupération des examens pour l'étudiant"""
    print("\n📚 Test de récupération des examens étudiants")
    print("=" * 50)
    
    # D'abord, se connecter
    login_data = {
        "username": "student@test.com",
        "password": "student123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            user_id = response.json().get('user_id')
            
            print(f"🔑 Token obtenu pour l'utilisateur ID: {user_id}")
            
            # Récupérer les examens de l'étudiant
            exams_response = requests.get(
                f"{API_BASE}/students/{user_id}/exams",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if exams_response.status_code == 200:
                exams = exams_response.json()
                print(f"✅ {len(exams)} examen(s) trouvé(s) pour l'étudiant")
                
                for exam in exams:
                    print(f"   📝 {exam.get('title', 'Sans titre')}")
                    print(f"      Durée: {exam.get('duration_minutes', 0)} minutes")
                    print(f"      Statut: {exam.get('exam_status', 'N/A')}")
                    
            else:
                print(f"❌ Erreur lors de la récupération des examens: {exams_response.status_code}")
                print(f"   Réponse: {exams_response.text}")
                
        else:
            print("❌ Impossible de se connecter pour tester les examens")
            
    except Exception as e:
        print(f"❌ Erreur lors du test des examens: {e}")

def main():
    """Fonction principale"""
    print("🚀 Test d'authentification pour l'application desktop Electron")
    print("=" * 60)
    
    # Test de connexion
    if test_login():
        # Test des examens si la connexion réussit
        test_student_exams()
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés!")
    print("\n📝 Instructions pour l'application desktop:")
    print("1. Utilisez l'email: student@test.com")
    print("2. Utilisez le mot de passe: student123")
    print("3. L'application devrait se connecter automatiquement")

if __name__ == "__main__":
    main()
