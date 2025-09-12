#!/usr/bin/env python3
"""
Script de test pour l'authentification desktop
"""

import requests
import json

API_BASE = "http://localhost:8000/api/v1"

def test_auth_endpoints():
    """Test des endpoints d'authentification"""
    print("🧪 Test des endpoints d'authentification")
    print("=" * 50)
    
    # Test 1: Login avec identifiants existants
    print("\n1. Test de login avec identifiants existants...")
    try:
        login_data = {
            "username": "student@test.com",
            "password": "password"
        }
        
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login réussi:")
            print(f"   - Token: {data.get('access_token', 'N/A')}")
            print(f"   - Utilisateur: {data.get('user', {}).get('username', 'N/A')}")
            print(f"   - Rôle: {data.get('user', {}).get('role', 'N/A')}")
        else:
            print(f"❌ Erreur login: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 2: Inscription d'un nouvel utilisateur
    print("\n2. Test d'inscription d'un nouvel utilisateur...")
    try:
        register_data = {
            "email": "test_desktop@example.com",
            "username": "test_desktop",
            "full_name": "Test Desktop User",
            "password": "password123",
            "role": "student",
            "face_image_base64": "fake_face_data_for_testing"
        }
        
        response = requests.post(f"{API_BASE}/auth/register-with-face", json=register_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Inscription réussie:")
            print(f"   - Token: {data.get('access_token', 'N/A')}")
            print(f"   - Utilisateur: {data.get('user', {}).get('username', 'N/A')}")
            print(f"   - Email: {data.get('user', {}).get('email', 'N/A')}")
        else:
            print(f"❌ Erreur inscription: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 3: Login avec le nouvel utilisateur
    print("\n3. Test de login avec le nouvel utilisateur...")
    try:
        login_data = {
            "username": "test_desktop@example.com",
            "password": "password123"
        }
        
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login avec nouvel utilisateur réussi:")
            print(f"   - Utilisateur: {data.get('user', {}).get('username', 'N/A')}")
        else:
            print(f"❌ Erreur login: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 4: Login avec visage (simulation)
    print("\n4. Test de login avec visage...")
    try:
        face_data = {
            "face_image_base64": "fake_face_data_for_testing"
        }
        
        response = requests.post(f"{API_BASE}/auth/login-with-face", json=face_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login avec visage réussi:")
            print(f"   - Utilisateur: {data.get('user', {}).get('username', 'N/A')}")
        else:
            print(f"❌ Erreur login visage: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Tests d'authentification terminés!")

if __name__ == "__main__":
    test_auth_endpoints()
