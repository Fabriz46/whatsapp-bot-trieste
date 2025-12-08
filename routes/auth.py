"""
Routes per autenticazione e gestione utenti
"""

from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from database import get_db_session, UserDB
from datetime import datetime, timedelta
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# ============================================================================
# MIDDLEWARE: Verifica autenticazione
# ============================================================================

def login_required(f):
    """Decorator per richiedere login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Non autenticato"}), 401
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# ROTTE AUTENTICAZIONE
# ============================================================================

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login API
    Riceve: username, password
    Ritorna: token sesione
    """
    
    db = get_db_session()
    
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    # Valida
    if not username or not password:
        return jsonify({"error": "Username e password obbligatori"}), 400
    
    # Cerca l'utente
    user = db.query(UserDB).filter(UserDB.username == username).first()
    
    if not user:
        db.close()
        return jsonify({"error": "Credenziali non valide"}), 401
    
    # Verifica che sia attivo
    if not user.attivo:
        db.close()
        return jsonify({"error": "Utente disabilitato"}), 401
    
    # Verifica password
    if not user.check_password(password):
        db.close()
        return jsonify({"error": "Credenziali non valide"}), 401
    
    # Aggiorna ultimo login
    user.ultimo_login = datetime.utcnow()
    db.commit()
    
    # Crea sessione
    session['user_id'] = user.id
    session['username'] = user.username
    session['ruolo'] = user.ruolo
    session.permanent = True  # La sessione persiste anche dopo chiusura browser
    
    db.close()
    
    return jsonify({
        "success": True,
        "message": f"✅ Benvenuto {user.nome_completo}!",
        "user": {
            "id": user.id,
            "username": user.username,
            "nome": user.nome_completo,
            "ruolo": user.ruolo
        }
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout - Distrugge la sessione"""
    
    username = session.get('username', 'Utente')
    
    session.clear()
    
    return jsonify({
        "success": True,
        "message": f"👋 Arrivederci {username}!"
    }), 200


@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Ritorna profilo dell'utente loggato"""
    
    db = get_db_session()
    user_id = session.get('user_id')
    
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    
    if not user:
        db.close()
        return jsonify({"error": "Utente non trovato"}), 404
    
    db.close()
    
    return jsonify({
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "nome": user.nome_completo,
            "ruolo": user.ruolo,
            "ultimo_login": user.ultimo_login.isoformat() if user.ultimo_login else None
        }
    })


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Cambia la password dell'utente"""
    
    db = get_db_session()
    user_id = session.get('user_id')
    
    data = request.json
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    
    # Valida
    if not old_password or not new_password:
        return jsonify({"error": "Password obbligatoria"}), 400
    
    if len(new_password) < 8:
        return jsonify({"error": "Password deve essere almeno 8 caratteri"}), 400
    
    # Cerca l'utente
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    
    if not user:
        db.close()
        return jsonify({"error": "Utente non trovato"}), 404
    
    # Verifica vecchia password
    if not user.check_password(old_password):
        db.close()
        return jsonify({"error": "Password attuale non corretta"}), 401
    
    # Imposta nuova password
    user.set_password(new_password)
    db.commit()
    db.close()
    
    return jsonify({
        "success": True,
        "message": "✅ Password cambiata con successo"
    }), 200


@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """
    Verifica lo stato di autenticazione (per il frontend)
    Ritorna True se loggato, False se no
    """
    
    if 'user_id' in session:
        return jsonify({
            "authenticated": True,
            "username": session.get('username'),
            "ruolo": session.get('ruolo')
        }), 200
    else:
        return jsonify({
            "authenticated": False
        }), 200
