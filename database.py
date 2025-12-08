"""
Database - Gestione del database PostgreSQL/SQLite
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config
from datetime import datetime
import bcrypt
import os

# ============================================================================
# CONFIGURAZIONE DATABASE
# ============================================================================

print(f"\n📦 Usando database: {Config.DATABASE_URL}")

# Crea il motore del database
engine = create_engine(
    Config.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"check_same_thread": False} if "sqlite" in Config.DATABASE_URL else {}
)

# Crea la sessione
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crea la classe Base per gli ORM
Base = declarative_base()

# ============================================================================
# MODELLI - DEFINISCI Base PRIMA!
# ============================================================================

class UserDB(Base):
    """
    Modello per gli utenti amministratori
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nome_completo = Column(String(120), default='')
    ruolo = Column(String(20), default='admin')  # admin, operator
    attivo = Column(Boolean, default=True)
    data_creazione = Column(DateTime, default=datetime.utcnow)
    ultimo_login = Column(DateTime, nullable=True)
    
    def set_password(self, password):
        """Hash della password con bcrypt"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Verifica la password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def __repr__(self):
        return f"<User {self.username}>"


class ClienteDB(Base):
    """
    Tabella CLIENTI - Dati di ogni cliente WhatsApp
    """
    __tablename__ = "clienti"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True)  # +393331234567
    nome = Column(String(100))
    azienda = Column(String(150))
    settore = Column(String(50))  # "finanza", "sport", "coworking", "generico"
    email = Column(String(100))
    etichette = Column(Text, default="")  # "VIP|Attivo"
    note = Column(Text, default="")
    data_creazione = Column(DateTime, default=datetime.utcnow)
    ultima_interazione = Column(DateTime, default=datetime.utcnow)
    numero_messaggi = Column(Integer, default=0)
    stato = Column(String(20), default="attivo")  # "attivo", "inattivo", "blocked"
    
    def __repr__(self):
        return f"<ClienteDB {self.nome} - {self.phone}>"


class FAQDB(Base):
    """
    Tabella FAQ - Domande frequenti e risposte
    """
    __tablename__ = "faq"
    
    id = Column(Integer, primary_key=True, index=True)
    domanda_keywords = Column(Text)  # "orari,apertura,quando"
    domanda_completa = Column(String(500))  # "A che ora siete aperti?"
    risposta = Column(Text)  # La risposta completa
    settore = Column(String(50), default="")  # "" = tutti, "sport" = solo sport
    priorita = Column(Integer, default=5)  # 1-10
    data_creazione = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<FAQDB {self.domanda_completa[:30]}...>"


class MessaggioDB(Base):
    """
    Tabella MESSAGGI - Log di tutti i messaggi scambiati
    """
    __tablename__ = "messaggi"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_phone = Column(String(20), index=True)
    testo_cliente = Column(Text)
    testo_risposta = Column(Text)
    tipo_risposta = Column(String(20))  # "faq" o "perplexity"
    data_messaggio = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MessaggioDB {self.id}>"


# ============================================================================
# INIZIALIZZAZIONE DATABASE
# ============================================================================

def init_db():
    """Inizializza il database creando tutte le tabelle"""
    try:
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database creato/connesso con successo")
        print(f"   Tabelle: users, clienti, faq, messaggi")
        
        # Crea utente admin
        crea_utente_predefinito()
        
    except Exception as e:
        print(f"❌ Errore database: {e}")
        raise


def crea_utente_predefinito():
    """
    Crea l'utente admin predefinito (se non esiste)
    Username: admin
    Password: trieste_bot_2025 (CAMBIA QUESTA!)
    """
    db = get_db_session()
    
    try:
        # Controlla se esiste già
        admin_esistente = db.query(UserDB).filter(UserDB.username == 'admin').first()
        
        if not admin_esistente:
            print("👤 Creazione utente admin predefinito...")
            
            admin = UserDB(
                username='admin',
                email='admin@trieste-facility.it',
                nome_completo='Amministratore',
                ruolo='admin',
                attivo=True
            )
            
            admin.set_password('trieste_bot_2025')  # ⚠️ CAMBIA QUESTA PASSWORD!
            
            db.add(admin)
            db.commit()
            
            print("✅ Utente admin creato!")
            print("   Username: admin")
            print("   Password: trieste_bot_2025")
            print("   ⚠️  CAMBIA LA PASSWORD AL PRIMO LOGIN!")
        else:
            print("✅ Utente admin già esistente")
    
    except Exception as e:
        print(f"❌ Errore creazione utente: {e}")
    finally:
        db.close()


# ============================================================================
# FUNZIONI HELPER
# ============================================================================

def get_db_session():
    """
    Crea una nuova sessione database.
    
    Uso:
        db = get_db_session()
        clienti = db.query(ClienteDB).all()
        db.close()
    """
    return SessionLocal()
