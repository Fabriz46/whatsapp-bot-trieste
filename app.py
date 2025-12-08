"""
WhatsApp Bot Trieste - App principale Flask
"""

from flask import Flask, jsonify, render_template, session, redirect
from routes.webhook import webhook_bp
from routes.dashboard_api import dashboard_api_bp
from routes.auth import auth_bp, login_required
from database import get_db_session, ClienteDB, FAQDB, MessaggioDB, init_db
from config import Config
import os
from datetime import datetime, timedelta
from utils.scheduler import start_scheduler, stop_scheduler

# Avvia lo scheduler
start_scheduler()

# Crea l'app Flask
app = Flask(__name__)

# Carica configurazione
app.config.from_object(Config)

# Imposta la chiave segreta per le sessioni
app.secret_key = Config.SECRET_KEY if hasattr(Config, 'SECRET_KEY') else 'dev-secret-key-change-in-production'

# Registra le blueprint
app.register_blueprint(webhook_bp)
app.register_blueprint(dashboard_api_bp)
app.register_blueprint(auth_bp)


# ============================================================================
# ROUTE PUBBLICHE
# ============================================================================

@app.route('/admin/scheduler/status', methods=['GET'])
@login_required
def scheduler_status():
    """Status dello scheduler"""
    from utils.scheduler import scheduler
    return jsonify({
        "running": scheduler.running,
        "jobs": len(scheduler.get_jobs()),
        "jobs_list": [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None
            }
            for job in scheduler.get_jobs()
        ]
    })


@app.route('/', methods=['GET'])
def home():
    """Home page - Mostra che il bot è online"""
    return jsonify({
        "status": "🟢 Bot operativo",
        "version": "1.0",
        "ambiente": Config.ENVIRONMENT,
        "webhook_url": "/webhook",
        "api_status": "/api/status",
        "login": "/login",
        "documentazione": "https://github.com/tuonome/whatsapp-bot-trieste"
    }), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check - Usato da Railway per controllare se il bot è vivo"""
    return jsonify({"status": "healthy"}), 200


@app.route('/login')
def login_page():
    """Pagina di login"""
    # Se già loggato, redirect a dashboard
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """Mostra la dashboard interattiva (protetta)"""
    return render_template('dashboard.html')


@app.route('/api/status', methods=['GET'])
def api_status():
    """Status del bot - mostra statistiche"""
    db = get_db_session()
    
    try:
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
    finally:
        db.close()


@app.route('/api/clienti', methods=['GET'])
def api_clienti():
    """Ritorna lista di tutti i clienti (JSON)"""
    db = get_db_session()
    
    try:
        clienti = db.query(ClienteDB).all()
        
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
    finally:
        db.close()


@app.route('/api/faq', methods=['GET'])
def api_faq():
    """Ritorna lista di tutte le FAQ (JSON)"""
    db = get_db_session()
    
    try:
        faq_list = db.query(FAQDB).all()
        
        return jsonify([{
            'id': f.id,
            'domanda': f.domanda_completa,
            'settore': f.settore if f.settore else 'Tutti',
            'priorita': f.priorita
        } for f in faq_list]), 200
    finally:
        db.close()


@app.route('/api/messaggi', methods=['GET'])
def api_messaggi():
    """Ritorna ultimi messaggi (JSON)"""
    db = get_db_session()
    
    try:
        messaggi = db.query(MessaggioDB).order_by(
            MessaggioDB.data_messaggio.desc()
        ).limit(20).all()
        
        return jsonify([{
            'id': m.id,
            'cliente': m.cliente_phone,
            'domanda': m.testo_cliente[:100],
            'risposta': m.testo_risposta[:100],
            'tipo': m.tipo_risposta,
            'data': m.data_messaggio.isoformat()
        } for m in messaggi]), 200
    finally:
        db.close()


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Pagina non trovata"""
    return jsonify({"error": "Route not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Errore interno"""
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# AVVIO
# ============================================================================

if __name__ == '__main__':
    # Inizializza il database
    init_db()
    
    print("\n" + "="*70)
    print("🚀 WHATSAPP BOT TRIESTE")
    print("="*70)
    print(f"🌐 Server: http://localhost:{Config.PORT}")
    print(f"🔐 Login: http://localhost:{Config.PORT}/login")
    print(f"📊 Dashboard: http://localhost:{Config.PORT}/dashboard")
    print(f"📍 Webhook: http://localhost:{Config.PORT}/webhook")
    print(f"📈 Status: http://localhost:{Config.PORT}/api/status")
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
