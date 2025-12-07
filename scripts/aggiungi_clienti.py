"""
Script per aggiungere clienti al database
"""

import sys
sys.path.insert(0, '.')

from database import get_db_session, ClienteDB
from datetime import datetime

def aggiungi_cliente(phone, nome, azienda="", settore="generico", email=""):
    """
    Aggiunge un cliente al database
    
    Parametri:
    - phone: numero WhatsApp (es: +393331234567)
    - nome: nome cliente
    - azienda: azienda (opzionale)
    - settore: finanza/sport/coworking/generico
    - email: email (opzionale)
    """
    
    db = get_db_session()
    
    # Controlla se esiste già
    cliente_esistente = db.query(ClienteDB).filter(
        ClienteDB.phone == phone
    ).first()
    
    if cliente_esistente:
        print(f"⚠️  Cliente {phone} esiste già")
        db.close()
        return
    
    # Crea nuovo cliente
    nuovo_cliente = ClienteDB(
        phone=phone,
        nome=nome,
        azienda=azienda,
        settore=settore,
        email=email,
        data_creazione=datetime.utcnow(),
        ultima_interazione=datetime.utcnow()
    )
    
    # Salva nel database
    db.add(nuovo_cliente)
    db.commit()
    
    print(f"✅ Cliente aggiunto: {nome} ({phone})")
    db.close()

def aggiungi_clienti_di_prova():
    """Aggiunge clienti di test"""
    
    print("\n" + "="*70)
    print("➕ AGGIUNTA CLIENTI DI PROVA")
    print("="*70 + "\n")
    
    # Aggiungi 3 clienti di prova
    clienti = [
        {
            "phone": "+393331234567",
            "nome": "Mario Rossi",
            "azienda": "Rossi & Co",
            "settore": "finanza",
            "email": "mario@rossi.it"
        },
        {
            "phone": "+393339876543",
            "nome": "Giulia Bianchi",
            "azienda": "Sport Club Trieste",
            "settore": "sport",
            "email": "giulia@sportclub.it"
        },
        {
            "phone": "+393335551111",
            "nome": "Luca Verdi",
            "azienda": "Tech Startup",
            "settore": "coworking",
            "email": "luca@startup.it"
        }
    ]
    
    for cliente in clienti:
        aggiungi_cliente(**cliente)
    
    print("\n" + "="*70)
    print("✅ Clienti aggiunti con successo!")
    print("="*70 + "\n")

if __name__ == "__main__":
    aggiungi_clienti_di_prova()
