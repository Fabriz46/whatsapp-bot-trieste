"""
API Dashboard - CRUD completo per Clienti e FAQ
Gestisce tutte le operazioni da dashboard
"""

from flask import Blueprint, request, jsonify, session
from database import get_db_session, ClienteDB, FAQDB
from datetime import datetime
from functools import wraps

dashboard_api_bp = Blueprint('dashboard_api', __name__, url_prefix='/api/dashboard')

# MIDDLEWARE: Verifica autenticazione
def require_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Non autenticato"}), 401
        return f(*args, **kwargs)
    return decorated

# ============================================================================
# GESTIONE CLIENTI
# ============================================================================

@dashboard_api_bp.route('/clienti', methods=['GET'])
@require_login
def get_clienti():
    """Ritorna lista di tutti i clienti con filtri"""
    
    db = get_db_session()
    
    # Parametri query
    pagina = request.args.get('pagina', 1, type=int)
    limite = request.args.get('limite', 20, type=int)
    settore = request.args.get('settore', '', type=str)
    ricerca = request.args.get('ricerca', '', type=str)
    
    query = db.query(ClienteDB)
    
    # Filtri
    if settore:
        query = query.filter(ClienteDB.settore == settore)
    
    if ricerca:
        query = query.filter(
            (ClienteDB.nome.ilike(f"%{ricerca}%")) |
            (ClienteDB.phone.ilike(f"%{ricerca}%")) |
            (ClienteDB.email.ilike(f"%{ricerca}%"))
        )
    
    # Paginazione
    totale = query.count()
    clienti = query.offset((pagina - 1) * limite).limit(limite).all()
    
    return jsonify({
        "success": True,
        "totale": totale,
        "pagina": pagina,
        "limite": limite,
        "clienti": [
            {
                "id": c.id,
                "phone": c.phone,
                "nome": c.nome,
                "azienda": c.azienda,
                "settore": c.settore,
                "email": c.email,
                "etichette": c.etichette,
                "numero_messaggi": c.numero_messaggi,
                "stato": c.stato,
                "data_creazione": c.data_creazione.isoformat() if c.data_creazione else None,
                "ultima_interazione": c.ultima_interazione.isoformat() if c.ultima_interazione else None,
            }
            for c in clienti
        ]
    })

@dashboard_api_bp.route('/clienti', methods=['POST'])
@require_login
def crea_cliente():
    """Crea nuovo cliente"""
    
    db = get_db_session()
    
    data = request.json
    
    # Valida
    if not data.get('phone'):
        return jsonify({"error": "Phone obbligatorio"}), 400
    
    phone = data.get('phone')
    if not phone.startswith('+'):
        phone = '+' + phone
    
    # Controlla duplicati
    esistente = db.query(ClienteDB).filter(ClienteDB.phone == phone).first()
    if esistente:
        return jsonify({"error": "Cliente già esiste"}), 409
    
    # Crea
    cliente = ClienteDB(
        phone=phone,
        nome=data.get('nome', 'N/A'),
        azienda=data.get('azienda', ''),
        settore=data.get('settore', 'generico'),
        email=data.get('email', ''),
        etichette=data.get('etichette', ''),
        note=data.get('note', ''),
        data_creazione=datetime.utcnow(),
        ultima_interazione=datetime.utcnow(),
        numero_messaggi=0,
        stato='attivo'
    )
    
    db.add(cliente)
    db.commit()
    
    return jsonify({
        "success": True,
        "message": f"Cliente {data.get('nome')} creato",
        "cliente_id": cliente.id
    }), 201

@dashboard_api_bp.route('/clienti/<int:cliente_id>', methods=['GET'])
@require_login
def get_cliente(cliente_id):
    """Ritorna dettagli cliente"""
    
    db = get_db_session()
    cliente = db.query(ClienteDB).filter(ClienteDB.id == cliente_id).first()
    
    if not cliente:
        return jsonify({"error": "Cliente non trovato"}), 404
    
    return jsonify({
        "success": True,
        "cliente": {
            "id": cliente.id,
            "phone": cliente.phone,
            "nome": cliente.nome,
            "azienda": cliente.azienda,
            "settore": cliente.settore,
            "email": cliente.email,
            "etichette": cliente.etichette,
            "note": cliente.note,
            "numero_messaggi": cliente.numero_messaggi,
            "stato": cliente.stato,
            "data_creazione": cliente.data_creazione.isoformat(),
            "ultima_interazione": cliente.ultima_interazione.isoformat(),
        }
    })

@dashboard_api_bp.route('/clienti/<int:cliente_id>', methods=['PUT'])
@require_login
def aggiorna_cliente(cliente_id):
    """Aggiorna cliente"""
    
    db = get_db_session()
    cliente = db.query(ClienteDB).filter(ClienteDB.id == cliente_id).first()
    
    if not cliente:
        return jsonify({"error": "Cliente non trovato"}), 404
    
    data = request.json
    
    # Aggiorna i campi
    if 'nome' in data:
        cliente.nome = data['nome']
    if 'azienda' in data:
        cliente.azienda = data['azienda']
    if 'settore' in data:
        cliente.settore = data['settore']
    if 'email' in data:
        cliente.email = data['email']
    if 'etichette' in data:
        cliente.etichette = data['etichette']
    if 'note' in data:
        cliente.note = data['note']
    if 'stato' in data:
        cliente.stato = data['stato']
    
    db.commit()
    
    return jsonify({
        "success": True,
        "message": f"Cliente {cliente.nome} aggiornato"
    })

@dashboard_api_bp.route('/clienti/<int:cliente_id>', methods=['DELETE'])
@require_login
def elimina_cliente(cliente_id):
    """Elimina cliente"""
    
    db = get_db_session()
    cliente = db.query(ClienteDB).filter(ClienteDB.id == cliente_id).first()
    
    if not cliente:
        return jsonify({"error": "Cliente non trovato"}), 404
    
    nome = cliente.nome
    db.delete(cliente)
    db.commit()
    
    return jsonify({
        "success": True,
        "message": f"Cliente {nome} eliminato"
    })

# ============================================================================
# GESTIONE FAQ
# ============================================================================

@dashboard_api_bp.route('/faq', methods=['GET'])
@require_login
def get_faq():
    """Ritorna lista FAQ con filtri"""
    
    db = get_db_session()
    
    pagina = request.args.get('pagina', 1, type=int)
    limite = request.args.get('limite', 20, type=int)
    settore = request.args.get('settore', '', type=str)
    ricerca = request.args.get('ricerca', '', type=str)
    
    query = db.query(FAQDB)
    
    if settore:
        query = query.filter(FAQDB.settore == settore)
    
    if ricerca:
        query = query.filter(
            (FAQDB.domanda_completa.ilike(f"%{ricerca}%")) |
            (FAQDB.domanda_keywords.ilike(f"%{ricerca}%"))
        )
    
    totale = query.count()
    faq_list = query.offset((pagina - 1) * limite).limit(limite).all()
    
    return jsonify({
        "success": True,
        "totale": totale,
        "pagina": pagina,
        "limite": limite,
        "faq": [
            {
                "id": f.id,
                "domanda_completa": f.domanda_completa,
                "domanda_keywords": f.domanda_keywords,
                "risposta": f.risposta,
                "settore": f.settore,
                "priorita": f.priorita,
                "data_creazione": f.data_creazione.isoformat() if f.data_creazione else None,
            }
            for f in faq_list
        ]
    })

@dashboard_api_bp.route('/faq', methods=['POST'])
@require_login
def crea_faq():
    """Crea nuova FAQ"""
    
    db = get_db_session()
    data = request.json
    
    if not data.get('domanda_completa') or not data.get('risposta'):
        return jsonify({"error": "Domanda e risposta obbligatori"}), 400
    
    faq = FAQDB(
        domanda_completa=data.get('domanda_completa'),
        domanda_keywords=data.get('domanda_keywords', ''),
        risposta=data.get('risposta'),
        settore=data.get('settore', ''),
        priorita=data.get('priorita', 5),
        data_creazione=datetime.utcnow()
    )
    
    db.add(faq)
    db.commit()
    
    return jsonify({
        "success": True,
        "message": "FAQ creata",
        "faq_id": faq.id
    }), 201

@dashboard_api_bp.route('/faq/<int:faq_id>', methods=['GET'])
@require_login
def get_faq_detail(faq_id):
    """Ritorna dettagli FAQ"""
    
    db = get_db_session()
    faq = db.query(FAQDB).filter(FAQDB.id == faq_id).first()
    
    if not faq:
        return jsonify({"error": "FAQ non trovata"}), 404
    
    return jsonify({
        "success": True,
        "faq": {
            "id": faq.id,
            "domanda_completa": faq.domanda_completa,
            "domanda_keywords": faq.domanda_keywords,
            "risposta": faq.risposta,
            "settore": faq.settore,
            "priorita": faq.priorita,
            "data_creazione": faq.data_creazione.isoformat(),
        }
    })

@dashboard_api_bp.route('/faq/<int:faq_id>', methods=['PUT'])
@require_login
def aggiorna_faq(faq_id):
    """Aggiorna FAQ"""
    
    db = get_db_session()
    faq = db.query(FAQDB).filter(FAQDB.id == faq_id).first()
    
    if not faq:
        return jsonify({"error": "FAQ non trovata"}), 404
    
    data = request.json
    
    if 'domanda_completa' in data:
        faq.domanda_completa = data['domanda_completa']
    if 'domanda_keywords' in data:
        faq.domanda_keywords = data['domanda_keywords']
    if 'risposta' in data:
        faq.risposta = data['risposta']
    if 'settore' in data:
        faq.settore = data['settore']
    if 'priorita' in data:
        faq.priorita = data['priorita']
    
    db.commit()
    
    return jsonify({
        "success": True,
        "message": "FAQ aggiornata"
    })

@dashboard_api_bp.route('/faq/<int:faq_id>', methods=['DELETE'])
@require_login
def elimina_faq(faq_id):
    """Elimina FAQ"""
    
    db = get_db_session()
    faq = db.query(FAQDB).filter(FAQDB.id == faq_id).first()
    
    if not faq:
        return jsonify({"error": "FAQ non trovata"}), 404
    
    domanda = faq.domanda_completa
    db.delete(faq)
    db.commit()
    
    return jsonify({
        "success": True,
        "message": f"FAQ eliminata"
    })

# ============================================================================
# STATISTICHE
# ============================================================================

@dashboard_api_bp.route('/stats', methods=['GET'])
@require_login
def get_stats():
    """Ritorna statistiche dashboard"""
    
    db = get_db_session()
    
    tot_clienti = db.query(ClienteDB).count()
    tot_faq = db.query(FAQDB).count()
    clienti_attivi = db.query(ClienteDB).filter(ClienteDB.stato == 'attivo').count()
    
    # Media messaggi per cliente
    media_msg = db.query(ClienteDB).filter(ClienteDB.numero_messaggi > 0).count()
    
    return jsonify({
        "success": True,
        "stats": {
            "clienti_totali": tot_clienti,
            "clienti_attivi": clienti_attivi,
            "faq_totali": tot_faq,
            "clienti_con_messaggi": media_msg,
        }
    })
