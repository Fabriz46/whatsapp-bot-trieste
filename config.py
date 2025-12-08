"""
Configurazione Bot - Impostazioni principali
"""

import os
from dotenv import load_dotenv

# Carica variabili da file .env
load_dotenv()

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================

SMTP_SERVER = os.getenv('SMTP_SERVER', '')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_FROM = os.getenv('SMTP_FROM', 'noreply@trieste-facility.it')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@trieste-facility.it')

# Opzionale: Webhook esterno
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')


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
