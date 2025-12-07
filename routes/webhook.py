"""
Webhook per ricevere messaggi WhatsApp
Questo è il "cuore" del bot
"""

from flask import request, jsonify, Blueprint
from datetime import datetime
from fuzzywuzzy import fuzz
import requests
import json

# Importa il database e i modelli
from database import get_db_session, ClienteDB, FAQDB, MessaggioDB

# Importa Perplexity
from utils.perplexity import chiama_perplexity

# Importa config
from config import Config

# Crea il blueprint (raccolta di route)
webhook_bp = Blueprint('webhook', __name__)

# ===== FUNZIONI HELPER =====

def invia_messaggio_whatsapp(numero_destinatario, testo):
    """
    Invia un messaggio WhatsApp via API Meta.
    
    Parametri:
    - numero_destinatario: es +393331234567
    - testo: il messaggio da inviare
    
    Ritorna True se mandato, False se errore
    """
    
    print(f"\n   📨 Invio messaggio a {numero_destinatario}")
    print(f"      Testo: {testo[:60]}...")
    
    # Se non hai token WhatsApp, simula l'invio (per testing)
    if not Config.WHATSAPP_TOKEN or Config.WHATSAPP_TOKEN == "":
        print(f"   ⚠️  Token WhatsApp non configurato - simulazione invio")
        return True
    
    # URL dell'API Meta
    url = f"{Config.WHATSAPP_API_URL}/{Config.WHATSAPP_PHONE_ID}/messages"
    
    # Prepara il messaggio
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero_destinatario,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": testo
        }
    }
    
    # Intestazioni HTTP
    headers = {
        "Authorization": f"Bearer {Config.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # Manda la richiesta
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        
        if response.status_code == 200:
            print(f"   ✅ Messaggio inviato")
            return True
        else:
            print(f"   ❌ Errore invio ({response.status_code})")
            return False
    
    except Exception as e:
        print(f"   ❌ Errore connessione: {e}")
        return False

def trova_faq_match(testo_messaggio, settore_cliente=""):
    """
    Cerca una FAQ che corrisponde al messaggio usando fuzzy matching.
    
    Fuzzy matching = trova somiglianze anche se non è esatto al 100%
    Es: "quando aprite" → trova "orari"
    
    Ritorna: (faq_trovata, score_percentuale)
    """
    
    # Apri connessione database
    db = get_db_session()
    
    # Prendi tutte le FAQ per questo settore
    faq_query = db.query(FAQDB)
    
    # Filtra per settore (include FAQ generiche "")
    faq_list = faq_query.filter(
        (FAQDB.settore == "") | (FAQDB.settore == settore_cliente)
    ).order_by(FAQDB.priorita.desc()).all()  # Ordina per priorità
    
    print(f"   🔍 Ricerca FAQ...")
    print(f"      Settore cliente: {settore_cliente}")
    print(f"      FAQ disponibili: {len(faq_list)}")
    
    migliore_match = None
    migliore_score = 0
    
    # Prova ogni FAQ
    for faq in faq_list:
        # Ogni FAQ ha parole chiave separate da virgola
        for keyword in faq.domanda_keywords.split(","):
            keyword = keyword.strip().lower()
            messaggio_lower = testo_messaggio.lower()
            
            # Calcola somiglianza tra messaggio e keyword (0-100)
            score = fuzz.partial_ratio(messaggio_lower, keyword)
            
            # Aggiorna se è il migliore trovato
            if score > migliore_score:
                migliore_score = score
                migliore_match = faq
    
    db.close()
    
    return migliore_match, migliore_score

# ===== ROUTE WEBHOOK =====

@webhook_bp.route('/webhook', methods=['GET'])
def webhook_verify():
    """
    Meta fa una richiesta GET per verificare che il webhook sia tuo.
    
    Devi ritornare il "challenge" che Meta ti invia.
    Se i token non match, ritorna errore 403.
    """
    
    verify_token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    print(f"\n🔐 Verificazione webhook")
    print(f"   Token ricevuto: {verify_token}")
    
    if verify_token == Config.WHATSAPP_VERIFY_TOKEN:
        print(f"   ✅ Token corretto!")
        return challenge, 200
    else:
        print(f"   ❌ Token sbagliato!")
        return "Unauthorized", 403

@webhook_bp.route('/webhook', methods=['POST'])
def webhook_handle_messages():
    """
    Riceve messaggi WhatsApp da Meta e risponde.
    
    FLOW:
    1. Cliente manda messaggio su WhatsApp
    2. Meta lo invia al webhook
    3. Noi lo processiamo
    4. Cerchiamo FAQ che corrisponde
    5. Se non trova → chiama Perplexity AI
    6. Inviamo risposta al cliente
    7. Salviamo nel database per log
    """
    
    print("\n" + "="*70)
    print("🔔 NUOVO MESSAGGIO RICEVUTO")
    print("="*70)
    
    # Prendi il JSON che Meta ci invia
    data = request.json
    
    # Controlla se c'è almeno una entry
    if not data.get("entry"):
        print("❌ Nessuna entry nel messaggio")
        return jsonify({"status": "ok"}), 200
    
    try:
        # Itera attraverso le entry (di solito ce n'è solo una)
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                
                # Controlla che sia un messaggio (non status o altro)
                if change.get("field") != "messages":
                    continue
                
                # Estrai il valore (dati del messaggio)
                value = change.get("value", {})
                
                # Ottieni info del cliente
                contacts = value.get("contacts", [{}])
                messages = value.get("messages", [{}])
                
                if not contacts or not messages:
                    print("❌ No contacts or messages")
                    continue
                
                # Estrai i dati
                numero_cliente = contacts[0].get("wa_id", "")

                # Meta manda numero SENZA +, aggiungiamo noi
                if numero_cliente and not numero_cliente.startswith("+"):
                    numero_cliente = "+" + numero_cliente

                nome_cliente = contacts[0].get("profile", {}).get("name", "Sconosciuto")
                messaggio_testo = messages[0].get("text", {}).get("body", "").strip()
                
                print(f"\n👤 Cliente: {nome_cliente} ({numero_cliente})")
                print(f"💬 Messaggio: {messaggio_testo}")
                
                if not numero_cliente or not messaggio_testo:
                    print("❌ Missing phone or text")
                    continue
                
                # ===== LOGICA PRINCIPALE =====
                
                # 1. CERCA O CREA CLIENTE NEL DATABASE
                db = get_db_session()
                cliente = db.query(ClienteDB).filter(
                    ClienteDB.phone == numero_cliente
                ).first()
                
                if not cliente:
                    # Nuovo cliente!
                    print(f"\n➕ NUOVO CLIENTE!")
                    cliente = ClienteDB(
                        phone=numero_cliente,
                        nome=nome_cliente,
                        settore="generico",
                        data_creazione=datetime.utcnow(),
                        ultima_interazione=datetime.utcnow(),
                        numero_messaggi=1
                    )
                    db.add(cliente)
                else:
                    # Cliente esistente - aggiorna dati
                    print(f"\n👋 Cliente esistente")
                    cliente.ultima_interazione = datetime.utcnow()
                    cliente.numero_messaggi += 1
                
                db.commit()
                
                # 2. PROVA A TROVARE FAQ CHE CORRISPONDA
                faq_trovata, score = trova_faq_match(messaggio_testo, cliente.settore)
                
                print(f"\n🔍 Risultato ricerca FAQ:")
                
                if faq_trovata and score > Config.FUZZY_MATCH_THRESHOLD:
                    # ✅ FAQ TROVATA!
                    print(f"   ✅ FAQ trovata! ({score}% similitudine)")
                    print(f"   Domanda: {faq_trovata.domanda_completa}")
                    risposta = faq_trovata.risposta
                    tipo_risposta = "faq"
                else:
                    # ❌ NESSUN FAQ MATCH - USA PERPLEXITY AI
                    print(f"   ❌ Nessun FAQ ({score}% < {Config.FUZZY_MATCH_THRESHOLD}%)")
                    contesto = f"Cliente: {cliente.nome}, Settore: {cliente.settore}, Azienda: {cliente.azienda}"
                    risposta = chiama_perplexity(messaggio_testo, contesto)
                    tipo_risposta = "perplexity"
                
                # 3. INVIA RISPOSTA WHATSAPP
                print(f"\n📤 Invio risposta...")
                invia_messaggio_whatsapp(numero_cliente, risposta)
                
                # 4. SALVA NEL DATABASE PER LOG
                nuovo_messaggio = MessaggioDB(
                    cliente_phone=numero_cliente,
                    testo_cliente=messaggio_testo,
                    testo_risposta=risposta,
                    tipo_risposta=tipo_risposta,
                    data_messaggio=datetime.utcnow()
                )
                db.add(nuovo_messaggio)
                db.commit()
                db.close()
                
                print(f"\n✅ MESSAGGIO PROCESSATO CON SUCCESSO")
        
        return jsonify({"status": "ok"}), 200
    
    except Exception as e:
        print(f"\n❌ ERRORE NEL WEBHOOK:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500
