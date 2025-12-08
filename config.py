"""
Configurazione Bot - Impostazioni principali
"""

import os
from dotenv import load_dotenv

# Carica variabili da file .env
load_dotenv()

class Config:
    """Tutte le configurazioni del bot"""
    
    # ===== DATABASE =====
    # Caricato da database.py
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot_database.db")
    
    # ===== WHATSAPP API =====
    WHATSAPP_API_URL = "https://graph.facebook.com/v18.0"
    WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")
    WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
    WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "trieste_bot_2025")
    
    # ===== PERPLEXITY API =====
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
    PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
    
    # ===== IMPOSTAZIONI BOT =====
    # Quanto deve somigliare una domanda a una keyword per essere FAQ match
    FUZZY_MATCH_THRESHOLD = 70  # 0-100, >= significa match
    
    # ===== FLASK =====
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("DEBUG", "False") == "True"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # ===== PORT =====
    PORT = int(os.getenv("PORT", 5000))

print("✅ Config caricata correttamente")
