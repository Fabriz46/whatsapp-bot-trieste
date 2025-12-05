import os
from dotenv import load_dotenv

# Carica variabili da file .env
load_dotenv()

class Config:
    """Tutte le configurazioni del bot"""
    
    # ===== DATABASE =====
    # Questo lo configurerai domani su Railway
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")
    
    # ===== WHATSAPP API =====
    WHATSAPP_API_URL = "https://graph.instagram.com/v18.0"
    WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")
    WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
    WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "trieste_bot_2025")
    
    # ===== PERPLEXITY API =====
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
    PERPLEXITY_API_URL = "https://api.perplexity.ai/openai/v1/chat/completions"
    
    # ===== IMPOSTAZIONI BOT =====
    FUZZY_MATCH_THRESHOLD = 70  # Quanto deve somigliare per trovare FAQ
    
    # ===== FLASK =====
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("DEBUG", "False") == "True"
    
    print("✅ Config caricata correttamente")
