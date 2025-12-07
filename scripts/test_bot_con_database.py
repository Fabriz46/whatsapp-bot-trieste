"""
Test del bot usando il database reale
"""

import sys
sys.path.insert(0, '.')

import requests
import json

WEBHOOK_URL = "http://localhost:5000/webhook"

def invia_messaggio_test(numero, nome, testo):
    """Invia messaggio fake al webhook"""
    
    # Questo è il formato che Meta manda
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
    
    print(f"\n" + "="*70)
    print(f"📱 TEST MESSAGGIO")
    print(f"   Da: {nome} ({numero})")
    print(f"   Testo: {testo}")
    print("="*70)
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        print(f"\n✅ Risposta: {response.status_code}")
        if response.status_code == 200:
            print(f"   Success: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"\n❌ Errore connessione: {e}")

if __name__ == "__main__":
    print("\n🧪 TEST BOT CON DATABASE\n")
    
    # Test 1: FAQ Match (orari)
    print("\n" + "-"*70)
    print("TEST 1: FAQ Match - Domanda su orari")
    print("-"*70)
    invia_messaggio_test(
        numero="+393331234567",
        nome="Mario Rossi",
        testo="A che ora siete aperti domani?"
    )
    
    # Test 2: FAQ Match (prezzi)
    print("\n" + "-"*70)
    print("TEST 2: FAQ Match - Domanda su prezzi")
    print("-"*70)
    invia_messaggio_test(
        numero="+393339876543",
        nome="Giulia Bianchi",
        testo="Quanto costano le prenotazioni padel?"
    )
    
    # Test 3: Nuovo cliente
    print("\n" + "-"*70)
    print("TEST 3: Nuovo cliente")
    print("-"*70)
    invia_messaggio_test(
        numero="+393334445555",
        nome="Franco Gialli",
        testo="Ciao, mi piacerebbe prenotare uno spazio"
    )
    
    print("\n\n🎉 TEST COMPLETATI!\n")
