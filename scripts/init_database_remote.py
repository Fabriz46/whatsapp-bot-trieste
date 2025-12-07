"""
Script per creare tabelle su PostgreSQL remoto
"""

import sys
sys.path.insert(0, '.')

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Carica variabili d'ambiente
load_dotenv()

# Prendi la connection string
database_url = os.getenv("DATABASE_URL")

if not database_url:
    print("❌ DATABASE_URL non trovata in .env")
    print("   Devi aggiungere DATABASE_URL nel file .env")
    sys.exit(1)

print(f"\n📦 Connessione a: {database_url.split('@')[1] if '@' in database_url else 'database'}")

# Importa i modelli DOPO di aver settato DATABASE_URL
from database import Base, engine, ClienteDB, FAQDB, MessaggioDB

try:
    # Crea tutte le tabelle
    Base.metadata.create_all(bind=engine)
    
    print("\n✅ Tabelle create su PostgreSQL!")
    print("   • clienti")
    print("   • faq")
    print("   • messaggi")
    
except Exception as e:
    print(f"\n❌ Errore: {e}")
    sys.exit(1)
