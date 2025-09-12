#!/usr/bin/env python3
"""
Script de test pour l'authentification avec les vrais utilisateurs
"""

import requests
import json

API_BASE = "http://localhost:8000/api/v1"

def test_real_users():
    """Test avec les vrais utilisateurs de la base"""
    print("🧪 Test d'authentification avec les vrais utilisateurs")
    print("=" * 60)
    
    # Test 1: Login avec admin
    print("\n1. Test de login avec admin...")
    try:
        login_data = {
            "username": "admin@proctoflex.ai",
            "password": "admin123"
        }
        
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login admin réussi:")
            print(f"   - Utilisateur: {data.get('user', {}).get('username', 'N/A')}")
            print(f"   - Rôle: {data.get('user', {}).get('role', 'N/A')}")
        else:
            print(f"❌ Erreur login admin: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 2: Login avec student1
    print("\n2. Test de login avec student1...")
    try:
        login_data = {
            "username": "student@test.com",
            "password": "password"
        }
        
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login student1 réussi:")
            print(f"   - Utilisateur: {data.get('user', {}).get('username', 'N/A')}")
            print(f"   - Rôle: {data.get('user', {}).get('role', 'N/A')}")
        else:
            print(f"❌ Erreur login student1: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 3: Login avec testuser
    print("\n3. Test de login avec testuser...")
    try:
        login_data = {
            "username": "test@example.com",
            "password": "password"
        }
        
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login testuser réussi:")
            print(f"   - Utilisateur: {data.get('user', {}).get('username', 'N/A')}")
            print(f"   - Rôle: {data.get('user', {}).get('role', 'N/A')}")
        else:
            print(f"❌ Erreur login testuser: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 4: Login avec le nouvel utilisateur créé
    print("\n4. Test de login avec test_desktop...")
    try:
        login_data = {
            "username": "test_desktop@example.com",
            "password": "password123"
        }
        
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login test_desktop réussi:")
            print(f"   - Utilisateur: {data.get('user', {}).get('username', 'N/A')}")
            print(f"   - Rôle: {data.get('user', {}).get('role', 'N/A')}")
        else:
            print(f"❌ Erreur login test_desktop: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Tests d'authentification terminés!")

if __name__ == "__main__":
    test_real_users()
