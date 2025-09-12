#!/usr/bin/env python3
"""
Script de test pour le système de gestion des utilisateurs
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000/api/v1"

def test_users_endpoints():
    """Test des endpoints utilisateurs"""
    print("🧪 Test du système de gestion des utilisateurs")
    print("=" * 50)
    
    # Test 1: Récupérer les statistiques
    print("\n1. Test des statistiques utilisateurs...")
    try:
        response = requests.get(f"{API_BASE}/users/stats")
        if response.status_code == 200:
            stats = response.json()
            print("✅ Statistiques récupérées avec succès:")
            print(f"   - Total utilisateurs: {stats['total_users']}")
            print(f"   - Étudiants: {stats['students']}")
            print(f"   - Administrateurs: {stats['admins']}")
            print(f"   - Instructeurs: {stats['instructors']}")
            print(f"   - Actifs aujourd'hui: {stats['active_today']}")
        else:
            print(f"❌ Erreur: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 2: Récupérer la liste des utilisateurs
    print("\n2. Test de la liste des utilisateurs...")
    try:
        response = requests.get(f"{API_BASE}/users")
        if response.status_code == 200:
            users = response.json()
            print(f"✅ {len(users)} utilisateurs récupérés:")
            for user in users:
                print(f"   - {user['full_name']} ({user['email']}) - {user['role']}")
        else:
            print(f"❌ Erreur: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 3: Créer un nouvel utilisateur
    print("\n3. Test de création d'utilisateur...")
    try:
        new_user = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Utilisateur Test",
            "role": "student",
            "password": "test123",
            "is_active": True
        }
        
        response = requests.post(f"{API_BASE}/users", json=new_user)
        if response.status_code == 200:
            created_user = response.json()
            print(f"✅ Utilisateur créé avec succès: {created_user['full_name']} (ID: {created_user['id']})")
            
            # Test 4: Récupérer l'utilisateur créé
            print("\n4. Test de récupération d'utilisateur...")
            user_id = created_user['id']
            response = requests.get(f"{API_BASE}/users/{user_id}")
            if response.status_code == 200:
                user = response.json()
                print(f"✅ Utilisateur récupéré: {user['full_name']}")
            else:
                print(f"❌ Erreur lors de la récupération: {response.status_code}")
            
            # Test 5: Mettre à jour l'utilisateur
            print("\n5. Test de mise à jour d'utilisateur...")
            update_data = {
                "full_name": "Utilisateur Test Modifié",
                "role": "instructor"
            }
            response = requests.put(f"{API_BASE}/users/{user_id}", json=update_data)
            if response.status_code == 200:
                updated_user = response.json()
                print(f"✅ Utilisateur mis à jour: {updated_user['full_name']} - {updated_user['role']}")
            else:
                print(f"❌ Erreur lors de la mise à jour: {response.status_code}")
            
            # Test 6: Toggle du statut
            print("\n6. Test de changement de statut...")
            response = requests.patch(f"{API_BASE}/users/{user_id}/toggle-status")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Statut modifié: {result['message']}")
            else:
                print(f"❌ Erreur lors du changement de statut: {response.status_code}")
            
            # Test 7: Supprimer l'utilisateur
            print("\n7. Test de suppression d'utilisateur...")
            response = requests.delete(f"{API_BASE}/users/{user_id}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result['message']}")
            else:
                print(f"❌ Erreur lors de la suppression: {response.status_code}")
            
        else:
            print(f"❌ Erreur lors de la création: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Tests terminés!")

if __name__ == "__main__":
    test_users_endpoints()
