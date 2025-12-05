"""
WhatsApp Bot Trieste - App principale
"""

from flask import Flask, jsonify, render_template
from routes.webhook import webhook_bp
from config import Config
import os

# Crea l'applicazione Flask
app = Flask(__name__)

# Carica configurazione
app.config.from_object(Config)

# Registra il blueprint (le route)
app.register_blueprint(webhook_bp)

# ===== ROUTE PUBBLICHE =====

@app.route('/', methods=['GET'])
def home():
    """Home page - mostra che il bot è online"""
    return jsonify({
        "status": "🟢 Bot operativo",
        "version": "1.0",
        "ambiente": os.getenv("ENVIRONMENT", "development"),
        "documentazione": "https://github.com/tuonome/whatsapp-bot-trieste"
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Check se il bot è vivo"""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/status', methods=['GET'])
def api_status():
    """Status del bot - numero clienti, FAQ, etc"""
    from models.cliente import Cliente
    from models.faq import FAQ
    
    return jsonify({
        "status": "running",
        "clienti_totali": len(Cliente.tutti()),
        "faq_disponibili": len(FAQ.tutti()),
        "database": Config.DATABASE_URL
    }), 200

@app.route('/api/clienti', methods=['GET'])
def api_clienti():
    """Ritorna lista di tutti i clienti (in JSON)"""
    from models.cliente import Cliente
    
    clienti = Cliente.tutti()
    return jsonify([c.to_dict() for c in clienti]), 200

@app.route('/api/faq', methods=['GET'])
def api_faq():
    """Ritorna lista di tutte le FAQ"""
    from models.faq import FAQ
    
    faq_list = FAQ.tutti()
    return jsonify([f.to_dict() for f in faq_list]), 200

# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    """Pagina non trovata"""
    return jsonify({"error": "Route not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Errore interno del server"""
    return jsonify({"error": "Internal server error"}), 500

# ===== AVVIO =====

if __name__ == '__main__':
    # Determina porta da variabile d'ambiente o usa 5000
    port = int(os.getenv("PORT", 5000))
    
    print("\n" + "="*60)
    print("🚀 WHATSAPP BOT TRIESTE")
    print("="*60)
    print(f"🌐 Server avviato su http://localhost:{port}")
    print(f"📍 Webhook: http://localhost:{port}/webhook")
    print(f"📊 Status: http://localhost:{port}/api/status")
    print("="*60 + "\n")
    
    # Avvia il server Flask
    # debug=True ricarica il server se cambi il codice
    app.run(
        debug=True,
        host='0.0.0.0',
        port=port
    )
