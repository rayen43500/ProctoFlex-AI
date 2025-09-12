#!/usr/bin/env python3
"""
Test simple de connexion PostgreSQL
"""

import psycopg2
from psycopg2 import sql

def test_connection():
    """Test de connexion avec différentes configurations"""
    
    configs = [
        "postgresql://root:root@localhost:5432/proctoflex",
        "postgresql://root:root@127.0.0.1:5432/proctoflex",
        "postgresql://root:root@host.docker.internal:5432/proctoflex",
    ]
    
    for i, url in enumerate(configs, 1):
        print(f"\n🔗 Test {i}: {url}")
        try:
            conn = psycopg2.connect(url)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ Connexion réussie!")
            print(f"   Version: {version}")
            
            # Tester les tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            print(f"   Tables: {tables}")
            
            cursor.close()
            conn.close()
            return url
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    return None

if __name__ == "__main__":
    print("🧪 Test de connexion PostgreSQL")
    print("=" * 40)
    
    working_url = test_connection()
    
    if working_url:
        print(f"\n🎉 Connexion fonctionnelle trouvée!")
        print(f"URL à utiliser: {working_url}")
    else:
        print(f"\n❌ Aucune connexion fonctionnelle trouvée")
        print("Vérifiez que PostgreSQL est démarré et accessible")
