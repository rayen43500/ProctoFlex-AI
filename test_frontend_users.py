#!/usr/bin/env python3
"""
Script de test pour vérifier que le frontend peut récupérer les données utilisateurs
"""

import requests
import json
import time

def test_frontend_users():
    """Test de l'intégration frontend-backend pour les utilisateurs"""
    print("🧪 Test de l'intégration Frontend-Backend pour les utilisateurs")
    print("=" * 60)
    
    # Attendre que le frontend soit prêt
    print("\n1. Vérification du frontend...")
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend accessible sur http://localhost:3000")
        else:
            print(f"⚠️ Frontend répond avec le code {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend non accessible: {e}")
        return
    
    # Test des endpoints backend
    print("\n2. Test des endpoints backend...")
    
    # Test des utilisateurs
    try:
        response = requests.get("http://localhost:8000/api/v1/users")
        if response.status_code == 200:
            users = response.json()
            print(f"✅ {len(users)} utilisateurs récupérés du backend:")
            for user in users:
                print(f"   - {user['full_name']} ({user['email']}) - {user['role']} - Actif: {user['is_active']}")
        else:
            print(f"❌ Erreur backend utilisateurs: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion backend: {e}")
    
    # Test des statistiques
    try:
        response = requests.get("http://localhost:8000/api/v1/users/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Statistiques récupérées:")
            print(f"   - Total: {stats['total_users']}")
            print(f"   - Étudiants: {stats['students']}")
            print(f"   - Administrateurs: {stats['admins']}")
            print(f"   - Actifs aujourd'hui: {stats['active_today']}")
        else:
            print(f"❌ Erreur backend statistiques: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion backend: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Tests terminés!")
    print("\n📋 Instructions pour tester manuellement:")
    print("1. Ouvrir http://localhost:3000 dans le navigateur")
    print("2. Se connecter avec les identifiants admin")
    print("3. Cliquer sur 'Utilisateurs' dans le menu")
    print("4. Vérifier que les utilisateurs s'affichent correctement")
    print("5. Tester la création d'un nouvel utilisateur")

if __name__ == "__main__":
    test_frontend_users()
