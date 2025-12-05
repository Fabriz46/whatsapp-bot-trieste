"""
Script per testare il webhook senza WhatsApp reale
"""

import requests
import json

# L'URL dove il bot è in ascolto
WEBHOOK_URL = "http://localhost:5000/webhook"

def invia_messaggio_test(numero, nome, testo):
    """
    Simula un messaggio WhatsApp in arrivo
    """
    
    # Questo è il formato che Meta manda al webhook
    payload = {
        "entry": [{
            "changes": [{
                "field": "messages",
                "value": {
                    "contacts": [{
                        "wa_id": numero,
                        "profile": {
                            "name": nome
                        }
                    }],
                    "messages": [{
                        "type": "text",
                        "text": {
                            "body": testo
                        }
                    }]
                }
            }]
        }]
    }
    
    print(f"\n" + "="*60)
    print(f"📱 INVIO MESSAGGIO TEST")
    print(f"   Da: {nome} ({numero})")
    print(f"   Testo: {testo}")
    print(f"="*60)
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        print(f"\n✅ Risposta ricevuta: {response.status_code}")
        print(f"   Body: {response.json()}")
    except Exception as e:
        print(f"\n❌ Errore: {e}")

if __name__ == "__main__":
    print("\n🧪 TEST WEBHOOK BOT TRIESTE\n")
    
    # TEST 1: Domanda che corrisponde a FAQ
    print("\n" + "-"*60)
    print("TEST 1: FAQ Match (domanda sugli orari)")
    print("-"*60)
    invia_messaggio_test(
        numero="+393331234567",
        nome="Mario Rossi",
        testo="A che ora siete aperti domani?"
    )
    
    # TEST 2: Domanda che corrisponde a FAQ
    print("\n" + "-"*60)
    print("TEST 2: FAQ Match (domanda su prezzi)")
    print("-"*60)
    invia_messaggio_test(
        numero="+393339876543",
        nome="Giulia Bianchi",
        testo="Quanto costano le prenotazioni?"
    )
    
    # TEST 3: Domanda che NON corrisponde (farà Perplexity)
    print("\n" + "-"*60)
    print("TEST 3: Perplexity (domanda generica)")
    print("-"*60)
    invia_messaggio_test(
        numero="+393335551111",
        nome="Luca Verdi",
        testo="Mi consigliate un piano di training per il padel?"
    )
    
    print("\n\n🎉 TEST COMPLETATI!\n")
