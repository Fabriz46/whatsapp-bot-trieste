"""
Configurazione Database - Crea tabelle e connessioni
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# ===== IMPOSTAZIONE DATABASE =====
# Per adesso usiamo SQLite (file locale)
# Domani migriamo a PostgreSQL su Railway

# Percorso file database (nella cartella progetto)
DATABASE_FILE = "bot_database.db"

# Se la variabile d'ambiente DATABASE_URL esiste, usa quella (Railway)
# Altrimenti usa SQLite locale
if os.getenv("DATABASE_URL"):
    # Railway PostgreSQL (non lo usiamo adesso)
    DATABASE_URL = os.getenv("DATABASE_URL")
else:
    # SQLite locale
    DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

print(f"📦 Usando database: {DATABASE_URL}")

# Crea il motore (connessione al database)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Crea la sessione (modo per leggere/scrivere nel database)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crea la base per le tabelle
Base = declarative_base()

# ===== DEFINIZIONE TABELLE =====

class ClienteDB(Base):
    """
    Tabella CLIENTI
    
    Contiene i dati di ogni cliente WhatsApp
    """
    __tablename__ = "clienti"
    
    # Colonne della tabella
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True)  # +393331234567
    nome = Column(String(100))
    azienda = Column(String(150))
    settore = Column(String(50))  # "finanza", "sport", "coworking", "generico"
    email = Column(String(100))
    etichette = Column(Text, default="")  # JSON: ["VIP", "Attivo"]
    note = Column(Text, default="")
    data_creazione = Column(DateTime, default=datetime.utcnow)
    ultima_interazione = Column(DateTime, default=datetime.utcnow)
    numero_messaggi = Column(Integer, default=0)
    stato = Column(String(20), default="attivo")  # "attivo", "inattivo", "blocked"
    
    def __repr__(self):
        return f"<ClienteDB {self.nome} - {self.phone}>"

class FAQDB(Base):
    """
    Tabella FAQ
    
    Contiene le domande frequenti e risposte
    """
    __tablename__ = "faq"
    
    id = Column(Integer, primary_key=True, index=True)
    domanda_keywords = Column(Text)  # "orari,apertura,quando"
    domanda_completa = Column(String(500))  # "A che ora siete aperti?"
    risposta = Column(Text)  # La risposta completa
    settore = Column(String(50), default="")  # "" = tutti, "sport" = solo sport
    priorita = Column(Integer, default=5)  # 1-10, più alto = trovo prima
    data_creazione = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<FAQDB {self.id}>"

class MessaggioDB(Base):
    """
    Tabella MESSAGGI
    
    Log di tutti i messaggi scambiati
    """
    __tablename__ = "messaggi"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_phone = Column(String(20), index=True)  # Chi ha mandato
    testo_cliente = Column(Text)  # Cosa ha scritto
    testo_risposta = Column(Text)  # Cosa gli abbiamo risposto
    tipo_risposta = Column(String(20))  # "faq" o "perplexity"
    data_messaggio = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MessaggioDB {self.id}>"

# ===== CREA LE TABELLE =====
# Se le tabelle non esistono, le crea
Base.metadata.create_all(bind=engine)

print("✅ Database creato/connesso con successo")
print(f"   Tabelle: clienti, faq, messaggi")

# ===== FUNZIONI HELPER =====

def get_db_session():
    """
    Crea una nuova sessione database.
    Usala per leggere/scrivere dati.
    
    Uso:
        db = get_db_session()
        clienti = db.query(ClienteDB).all()
        db.close()
    """
    return SessionLocal()
