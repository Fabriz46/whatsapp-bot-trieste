"""
Webhook per ricevere messaggi WhatsApp
"""

from flask import request, jsonify, Blueprint
from datetime import datetime
from fuzzywuzzy import fuzz
from models.cliente import Cliente
from models.faq import FAQ
from utils.perplexity import chiama_perplexity
from config import Config
import requests

# Crea un "blueprint" (modulo route)
webhook_bp = Blueprint('webhook', __name__)

# ===== FUNZIONI HELPER =====

def invia_messaggio_whatsapp(numero_destinatario, testo):
    """
    Invia un messaggio WhatsApp via API Meta.
    
    Adesso NON funziona perché non hai token Meta ancora.
    Domani lo abiliterai.
    """
    
    print(f"\n📨 Invio a {numero_destinatario}:")
    print(f"   {testo[:100]}...")
    
    # Se non hai token, non mandare (siamo in test)
    if not Config.WHATSAPP_TOKEN or Config.WHATSAPP_TOKEN == "":
        print(f"⚠️  WhatsApp token non configurato - simulazione invio")
        return True
    
    url = f"{Config.WHATSAPP_API_URL}/{Config.WHATSAPP_PHONE_ID}/messages"
    
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
    
    headers = {
        "Authorization": f"Bearer {Config.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Messaggio inviato con successo")
            return True
        else:
            print(f"❌ Errore invio ({response.status_code}): {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Errore connessione WhatsApp: {e}")
        return False

def trova_faq_match(testo_messaggio, settore_cliente=""):
    """
    Cerca una FAQ che corrisponde al messaggio usando fuzzy matching.
    
    Fuzzy matching = trova somiglianze anche se non è uguale al 100%
    Es: "quando aprite" → trova "orari"
    """
    
    faq_list = FAQ.per_settore(settore_cliente)
    
    migliore_match = None
    migliore_score = 0
    
    for faq in faq_list:
        # Controlla ogni keyword della FAQ
        for keyword in faq.domanda_keywords.split(","):
            keyword = keyword.strip().lower()
            messaggio_lower = testo_messaggio.lower()
            
            # Calcola quanto il messaggio somiglia alla keyword (0-100)
            score = fuzz.partial_ratio(messaggio_lower, keyword)
            
            # Aggiorna se è il migliore trovato
            if score > migliore_score:
                migliore_score = score
                migliore_match = faq
    
    return migliore_match, migliore_score

# ===== ROUTE WEBHOOK =====

@webhook_bp.route('/webhook', methods=['GET'])
def webhook_verify():
    """
    Meta fa una richiesta GET per verificare che il webhook sia tuo.
    
    Devi ritornare il "challenge" che Meta ti invia.
    """
    
    verify_token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    print(f"\n🔐 Verificazione webhook:")
    print(f"   Token ricevuto: {verify_token}")
    print(f"   Challenge: {challenge}")
    
    if verify_token == Config.WHATSAPP_VERIFY_TOKEN:
        print(f"   ✅ Token corretto!")
        return challenge, 200
    else:
        print(f"   ❌ Token sbagliato!")
        return "Unauthorized", 403

@webhook_bp.route('/webhook', methods=['POST'])
def webhook_handle_messages():
    """
    Riceve messaggi WhatsApp da Meta.
    
    Flow:
    1. Cliente manda messaggio su WhatsApp
    2. Meta lo invia al nostro webhook
    3. Noi analizziamo il messaggio
    4. Cerchiamo una FAQ che corrisponde
    5. Se non trova → chiama Perplexity AI
    6. Inviamo la risposta al cliente
    """
    
    print("\n" + "="*60)
    print("🔔 NUOVO MESSAGGIO RICEVUTO")
    print("="*60)
    
    data = request.json
    
    # Controlla se c'è almeno una entry
    if not data.get("entry"):
        print("⚠️  No entry in data")
        return jsonify({"status": "ok"}), 200
    
    try:
        # Itera attraverso le entry (potrebbe averne più di una)
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                
                # Controlla se è un messaggio (potrebbe essere altro)
                if change.get("field") != "messages":
                    continue
                
                value = change.get("value", {})
                
                # Estrai informazioni del cliente
                contacts = value.get("contacts", [{}])
                messages = value.get("messages", [{}])
                
                if not contacts or not messages:
                    print("⚠️  No contacts or messages")
                    continue
                
                numero_cliente = contacts[0].get("wa_id", "")
                nome_cliente = contacts[0].get("profile", {}).get("name", "Sconosciuto")
                messaggio_testo = messages[0].get("text", {}).get("body", "").strip()
                
                print(f"\n👤 Cliente: {nome_cliente} ({numero_cliente})")
                print(f"💬 Messaggio: {messaggio_testo}")
                
                if not numero_cliente or not messaggio_testo:
                    print("⚠️  Missing phone or message text")
                    continue
                
                # ===== LOGICA PRINCIPALE =====
                
                # 1. TROVA O CREA CLIENTE NEL DB
                cliente = Cliente.trova_per_phone(numero_cliente)
                
                if not cliente:
                    print(f"➕ Nuovo cliente! Aggiunto al database")
                    cliente = Cliente(
                        phone=numero_cliente,
                        nome=nome_cliente,
                        settore="generico"
                    )
                    cliente.save()
                else:
                    print(f"👋 Cliente esistente")
                
                # Aggiorna statistiche cliente
                cliente.ultima_interazione = datetime.utcnow()
                cliente.numero_messaggi += 1
                
                # 2. PROVA A TROVARE FAQ CHE CORRISPONDA
                faq_trovata, score = trova_faq_match(messaggio_testo, cliente.settore)
                
                print(f"\n🔍 Ricerca FAQ...")
                
                if faq_trovata and score > Config.FUZZY_MATCH_THRESHOLD:
                    # FAQ TROVATA! Usa risposta template
                    print(f"   ✅ FAQ trovata! ({score}% similitudine)")
                    print(f"   Domanda: {faq_trovata.domanda_completa}")
                    risposta = faq_trovata.risposta
                else:
                    # NESSUN FAQ MATCH - USA PERPLEXITY
                    print(f"   ❌ Nessun FAQ con score sufficiente ({score}% < {Config.FUZZY_MATCH_THRESHOLD}%)")
                    print(f"   🤖 Chiamo Perplexity AI...")
                    contesto = f"Cliente: {cliente.nome}, Settore: {cliente.settore}"
                    risposta = chiama_perplexity(messaggio_testo, contesto)
                
                # 3. INVIA RISPOSTA WHATSAPP
                print(f"\n📤 Invio risposta...")
                invia_messaggio_whatsapp(numero_cliente, risposta)
                
                print(f"\n✅ MESSAGGIO PROCESSATO CON SUCCESSO")
        
        return jsonify({"status": "ok"}), 200
    
    except Exception as e:
        print(f"\n❌ ERRORE: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500
