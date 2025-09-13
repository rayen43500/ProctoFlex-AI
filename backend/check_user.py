#!/usr/bin/env python3
"""
Script pour vérifier et créer l'utilisateur de test
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.security import get_password_hash
from app.core.database import User

def check_and_create_user():
    """Vérifier et créer l'utilisateur de test"""
    try:
        # Créer l'engine
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("🔍 Vérification de l'utilisateur de test...")
        
        # Vérifier si l'utilisateur existe
        user = db.query(User).filter(User.email == "student@test.com").first()
        
        if user:
            print(f"✅ Utilisateur trouvé:")
            print(f"   ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Username: {user.username}")
            print(f"   Nom: {user.full_name}")
            print(f"   Rôle: {user.role}")
            print(f"   Actif: {user.is_active}")
        else:
            print("❌ Utilisateur non trouvé, création...")
            
            # Créer l'utilisateur
            hashed_password = get_password_hash("student123")
            new_user = User(
                email="student@test.com",
                username="student1",
                full_name="Étudiant Test",
                hashed_password=hashed_password,
                role="student",
                is_active=True
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            print(f"✅ Utilisateur créé:")
            print(f"   ID: {new_user.id}")
            print(f"   Email: {new_user.email}")
            print(f"   Username: {new_user.username}")
            print(f"   Nom: {new_user.full_name}")
            print(f"   Rôle: {new_user.role}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Vérification de l'utilisateur de test")
    print("=" * 40)
    
    if check_and_create_user():
        print("\n✅ Vérification terminée avec succès!")
    else:
        print("\n❌ Erreur lors de la vérification")
        sys.exit(1)
