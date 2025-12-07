"""
Script per aggiungere FAQ al database
"""

import sys
sys.path.insert(0, '.')

# Carica variabili d'ambiente PRIMA di importare database
from dotenv import load_dotenv
load_dotenv()

from database import get_db_session, FAQDB
from datetime import datetime

def aggiungi_faq(domanda_keywords, domanda_completa, risposta, settore="", priorita=5):
    """
    Aggiunge una FAQ al database
    
    Parametri:
    - domanda_keywords: parole chiave separate da virgola (es: "orari,apertura,quando")
    - domanda_completa: domanda intera (es: "A che ora siete aperti?")
    - risposta: risposta completa
    - settore: "" per tutti, "sport" per sport, etc
    - priorita: 1-10, più alto = trova prima
    """
    
    db = get_db_session()
    
    nuova_faq = FAQDB(
        domanda_keywords=domanda_keywords,
        domanda_completa=domanda_completa,
        risposta=risposta,
        settore=settore,
        priorita=priorita,
        data_creazione=datetime.utcnow()
    )
    
    db.add(nuova_faq)
    db.commit()
    
    print(f"✅ FAQ aggiunta: {domanda_completa}")
    db.close()

def aggiungi_faq_di_prova():
    """Aggiunge FAQ di test"""
    
    print("\n" + "="*70)
    print("➕ AGGIUNTA FAQ DI PROVA")
    print("="*70 + "\n")
    
    faq_list = [
        {
            "domanda_keywords": "orari,apertura,quando,disponibilità,aperto,orario",
            "domanda_completa": "A che ora siete aperti?",
            "risposta": """📍 ORARI TRIESTE:
🕐 Lunedì-Venerdì: 9:00-18:00
🕐 Sabato: 9:00-13:00
🕐 Domenica: Chiuso

Per domande: +39 040 123456""",
            "settore": "",
            "priorita": 10
        },
        {
            "domanda_keywords": "prezzi,costo,quanto,tariffa,listino,price,tariffe",
            "domanda_completa": "Quanto costano i vostri servizi?",
            "risposta": """💰 TARIFFE:

💼 COWORKING:
   • Giornaliero: €20
   • Mensile: €200-400
   
🏓 PADEL:
   • Singola ora: €25
   • Abbonamento 10 ore: €200

📞 Contattaci per offerta personalizzata!""",
            "settore": "",
            "priorita": 9
        },
        {
            "domanda_keywords": "contatto,numero,telefono,mail,email,where,dove,indirizzo,address",
            "domanda_completa": "Come posso contattarvi?",
            "risposta": """📞 CONTATTI:

☎️ Telefono: +39 040 123456
📧 Email: info@trieste-facility.it
📍 Via Mezzo, 15 - Trieste
🌐 www.trieste-facility.it
📱 WhatsApp: questo numero!""",
            "settore": "",
            "priorita": 9
        },
        {
            "domanda_keywords": "disponibilità,libero,prenotare,booking,slot,prenoto,campo libero",
            "domanda_completa": "Come prenoto un campo padel?",
            "risposta": """🏓 PRENOTAZIONE PADEL:

1️⃣ Scrivi qui su WhatsApp
2️⃣ Dimmi giorno e ora preferiti
3️⃣ Noi confermiamo disponibilità
4️⃣ Paghi in loco (contanti/carta)

⏰ Orari disponibili: 
   Lun-Dom 9:00-20:00

Prenotare con almeno 2 ore di anticipo!""",
            "settore": "sport",
            "priorita": 9
        },
        {
            "domanda_keywords": "spazi,sale,riunioni,meeting,conferenza,workshop,evento",
            "domanda_completa": "Avete spazi per riunioni?",
            "risposta": """📋 SPAZI PER RIUNIONI:

✅ Sala Trieste (20 persone)
✅ Sala Meeting (10 persone)
✅ Sala Padel (area lounge)

SERVIZI INCLUSI:
   • WiFi veloce
   • Proiettore
   • Tavoli/sedie
   • Parcheggio gratuito

📞 Contatta per preventivo: +39 040 123456""",
            "settore": "coworking",
            "priorita": 8
        }
    ]
    
    for faq in faq_list:
        aggiungi_faq(**faq)
    
    print("\n" + "="*70)
    print("✅ FAQ aggiunte con successo!")
    print("="*70 + "\n")

if __name__ == "__main__":
    aggiungi_faq_di_prova()
