#!/usr/bin/env python3
"""
Script de vérification de la base de données ProctoFlex
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from app.core.config import settings

def check_connection():
    """Vérifier la connexion à la base de données"""
    try:
        print("🔗 Test de connexion à PostgreSQL...")
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connexion réussie!")
            print(f"   Version: {version}")
            
            # Vérifier la base de données
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"   Base de données: {db_name}")
            
        return True
        
    except OperationalError as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def check_tables():
    """Vérifier les tables"""
    try:
        print("\n📋 Vérification des tables...")
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Lister les tables
            result = conn.execute(text("""
                SELECT table_name, 
                       (SELECT count(*) FROM information_schema.columns 
                        WHERE table_name = t.table_name AND table_schema = 'public') as column_count
                FROM information_schema.tables t
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tables = result.fetchall()
            
            if tables:
                print(f"✅ {len(tables)} table(s) trouvée(s):")
                for table_name, column_count in tables:
                    print(f"   - {table_name} ({column_count} colonnes)")
            else:
                print("⚠️  Aucune table trouvée")
                
        return len(tables) > 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def check_data():
    """Vérifier les données"""
    try:
        print("\n📊 Vérification des données...")
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Compter les utilisateurs
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result.fetchone()[0]
                print(f"   Utilisateurs: {user_count}")
            except:
                print("   Utilisateurs: Table non trouvée")
            
            # Compter les examens
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM exams"))
                exam_count = result.fetchone()[0]
                print(f"   Examens: {exam_count}")
            except:
                print("   Examens: Table non trouvée")
            
            # Compter les sessions
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM exam_sessions"))
                session_count = result.fetchone()[0]
                print(f"   Sessions: {session_count}")
            except:
                print("   Sessions: Table non trouvée")
                
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def check_exam_fields():
    """Vérifier les nouveaux champs des examens"""
    try:
        print("\n🔍 Vérification des champs d'examen...")
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'exams' AND table_schema = 'public'
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            
            if columns:
                print("✅ Colonnes de la table exams:")
                for col_name, data_type, nullable in columns:
                    null_info = "NULL" if nullable == "YES" else "NOT NULL"
                    print(f"   - {col_name} ({data_type}) {null_info}")
                
                # Vérifier les nouveaux champs
                new_fields = ['instructions', 'status', 'pdf_path', 'updated_at']
                existing_fields = [col[0] for col in columns]
                
                missing_fields = [field for field in new_fields if field not in existing_fields]
                if missing_fields:
                    print(f"⚠️  Champs manquants: {missing_fields}")
                    print("   Exécutez: psql proctoflex < migrations/add_exam_fields.sql")
                else:
                    print("✅ Tous les nouveaux champs sont présents")
            else:
                print("❌ Table exams non trouvée")
                
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Fonction principale"""
    print("🔍 Vérification de la base de données ProctoFlex")
    print("=" * 50)
    
    # Vérifier la connexion
    if not check_connection():
        print("\n🔧 Solutions:")
        print("1. Démarrer PostgreSQL: docker-compose up postgres -d")
        print("2. Vérifier la configuration dans .env")
        print("3. Créer la base: createdb proctoflex")
        sys.exit(1)
    
    # Vérifier les tables
    if not check_tables():
        print("\n🔧 Solutions:")
        print("1. Exécuter: python setup_database.py")
        print("2. Ou: psql proctoflex < init.sql")
        sys.exit(1)
    
    # Vérifier les données
    check_data()
    
    # Vérifier les champs d'examen
    check_exam_fields()
    
    print("\n🎉 Vérification terminée!")

if __name__ == "__main__":
    main()
