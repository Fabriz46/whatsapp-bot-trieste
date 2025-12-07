"""
WhatsApp Bot Trieste - App principale Flask
"""

from flask import Flask, jsonify
from routes.webhook import webhook_bp
from database import get_db_session, ClienteDB, FAQDB, MessaggioDB
from config import Config
import os
from datetime import datetime, timedelta

# Crea l'app Flask
app = Flask(__name__)

# Carica configurazione
app.config.from_object(Config)

# Registra le route dal webhook
app.register_blueprint(webhook_bp)

# ===== ROUTE PUBBLICHE =====

@app.route('/', methods=['GET'])
def home():
    """
    Home page - Mostra che il bot è online
    """
    return jsonify({
        "status": "🟢 Bot operativo",
        "version": "1.0",
        "ambiente": Config.ENVIRONMENT,
        "webhook_url": "/webhook",
        "api_status": "/api/status",
        "documentazione": "https://github.com/tuonome/whatsapp-bot-trieste"
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check - Usato da Railway per controllare se il bot è vivo
    """
    return jsonify({"status": "healthy"}), 200

@app.route('/api/status', methods=['GET'])
def api_status():
    """
    Status del bot - mostra statistiche
    """
    db = get_db_session()
    
    # Conta clienti
    clienti_totali = db.query(ClienteDB).count()
    clienti_attivi = db.query(ClienteDB).filter(
        ClienteDB.stato == "attivo"
    ).count()
    
    # Conta FAQ
    faq_totali = db.query(FAQDB).count()
    
    # Conta messaggi oggi
    oggi = datetime.utcnow().date()
    messaggi_oggi = db.query(MessaggioDB).filter(
        MessaggioDB.data_messaggio >= datetime.combine(oggi, datetime.min.time())
    ).count()
    
    # Ultimi messaggi
    ultimi_messaggi = db.query(MessaggioDB).order_by(
        MessaggioDB.data_messaggio.desc()
    ).limit(5).all()
    
    db.close()
    
    return jsonify({
        "status": "running",
        "clienti": {
            "totali": clienti_totali,
            "attivi": clienti_attivi
        },
        "faq": {
            "totali": faq_totali
        },
        "messaggi": {
            "oggi": messaggi_oggi
        },
        "ultimi_messaggi": [
            {
                "cliente": m.cliente_phone,
                "domanda": m.testo_cliente[:50] + "...",
                "tipo": m.tipo_risposta,
                "data": m.data_messaggio.isoformat()
            }
            for m in ultimi_messaggi
        ]
    }), 200

@app.route('/api/clienti', methods=['GET'])
def api_clienti():
    """
    Ritorna lista di tutti i clienti (JSON)
    """
    db = get_db_session()
    clienti = db.query(ClienteDB).all()
    db.close()
    
    return jsonify([{
        'id': c.id,
        'phone': c.phone,
        'nome': c.nome,
        'azienda': c.azienda,
        'settore': c.settore,
        'numero_messaggi': c.numero_messaggi,
        'stato': c.stato,
        'ultima_interazione': c.ultima_interazione.isoformat()
    } for c in clienti]), 200

@app.route('/api/faq', methods=['GET'])
def api_faq():
    """
    Ritorna lista di tutte le FAQ (JSON)
    """
    db = get_db_session()
    faq_list = db.query(FAQDB).all()
    db.close()
    
    return jsonify([{
        'id': f.id,
        'domanda': f.domanda_completa,
        'settore': f.settore if f.settore else 'Tutti',
        'priorita': f.priorita
    } for f in faq_list]), 200

@app.route('/api/messaggi', methods=['GET'])
def api_messaggi():
    """
    Ritorna ultimi messaggi (JSON)
    """
    db = get_db_session()
    messaggi = db.query(MessaggioDB).order_by(
        MessaggioDB.data_messaggio.desc()
    ).limit(20).all()
    db.close()
    
    return jsonify([{
        'id': m.id,
        'cliente': m.cliente_phone,
        'domanda': m.testo_cliente[:100],
        'risposta': m.testo_risposta[:100],
        'tipo': m.tipo_risposta,
        'data': m.data_messaggio.isoformat()
    } for m in messaggi]), 200

# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    """Pagina non trovata"""
    return jsonify({"error": "Route not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Errore interno"""
    return jsonify({"error": "Internal server error"}), 500

# ===== AVVIO =====

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 WHATSAPP BOT TRIESTE")
    print("="*70)
    print(f"🌐 Server: http://localhost:{Config.PORT}")
    print(f"📍 Webhook: http://localhost:{Config.PORT}/webhook")
    print(f"📊 Status: http://localhost:{Config.PORT}/api/status")
    print(f"👥 Clienti: http://localhost:{Config.PORT}/api/clienti")
    print(f"❓ FAQ: http://localhost:{Config.PORT}/api/faq")
    print(f"💬 Messaggi: http://localhost:{Config.PORT}/api/messaggi")
    print("="*70 + "\n")
    
    # Avvia server
    app.run(
        debug=Config.DEBUG,
        host='0.0.0.0',
        port=Config.PORT
    )
