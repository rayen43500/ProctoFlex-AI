#!/usr/bin/env python3
"""
Script de configuration de la base de données ProctoFlex
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from app.core.config import settings
from app.core.database import Base, engine

def create_database():
    """Créer la base de données si elle n'existe pas"""
    try:
        # Extraire les informations de connexion
        db_url = settings.DATABASE_URL
        print(f"🔗 Connexion à la base de données: {db_url}")
        
        # Créer l'engine
        engine = create_engine(db_url)
        
        # Tester la connexion
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connexion réussie à PostgreSQL {version}")
            
        return True
        
    except OperationalError as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        print("\n🔧 Solutions possibles:")
        print("1. Vérifiez que PostgreSQL est démarré")
        print("2. Vérifiez les paramètres de connexion dans .env")
        print("3. Créez la base de données: createdb proctoflex")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def create_tables():
    """Créer toutes les tables"""
    try:
        print("\n📋 Création des tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables créées avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables: {e}")
        return False

def run_migrations():
    """Exécuter les migrations SQL"""
    try:
        print("\n🔄 Exécution des migrations...")
        
        # Lire le fichier d'initialisation
        with open('init.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Exécuter les commandes SQL
        with engine.connect() as conn:
            # Diviser le contenu en commandes individuelles
            commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
            
            for command in commands:
                if command:
                    try:
                        conn.execute(text(command))
                        conn.commit()
                    except Exception as e:
                        print(f"⚠️  Avertissement pour la commande: {command[:50]}... - {e}")
        
        print("✅ Migrations exécutées")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des migrations: {e}")
        return False

def check_tables():
    """Vérifier que les tables existent"""
    try:
        print("\n🔍 Vérification des tables...")
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print("✅ Tables trouvées:")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("⚠️  Aucune table trouvée")
                
        return len(tables) > 0
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Configuration de la base de données ProctoFlex")
    print("=" * 50)
    
    # Vérifier la connexion
    if not create_database():
        sys.exit(1)
    
    # Créer les tables
    if not create_tables():
        sys.exit(1)
    
    # Exécuter les migrations
    if not run_migrations():
        print("⚠️  Migrations échouées, mais les tables de base sont créées")
    
    # Vérifier les tables
    if not check_tables():
        print("⚠️  Problème avec les tables")
        sys.exit(1)
    
    print("\n🎉 Configuration terminée avec succès!")
    print("\n📝 Prochaines étapes:")
    print("1. Démarrer le serveur: python main.py")
    print("2. Tester l'API: python test_exam_system.py")
    print("3. Accéder à l'interface web")

if __name__ == "__main__":
    main()
