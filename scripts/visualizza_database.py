"""
Script per visualizzare contenuto database
Utile per debugging
"""

import sys
sys.path.insert(0, '.')

from database import get_db_session, ClienteDB, FAQDB, MessaggioDB

def visualizza_database():
    """Mostra tutto il database"""
    
    db = get_db_session()
    
    print("\n" + "="*70)
    print("📦 CONTENUTO DATABASE")
    print("="*70)
    
    # ===== CLIENTI =====
    print("\n👥 CLIENTI:")
    print("-"*70)
    clienti = db.query(ClienteDB).all()
    
    if not clienti:
        print("   (Nessun cliente ancora)")
    else:
        print(f"   Totale: {len(clienti)}")
        for cliente in clienti:
            print(f"\n   📱 {cliente.nome}")
            print(f"      Telefono: {cliente.phone}")
            print(f"      Azienda: {cliente.azienda}")
            print(f"      Settore: {cliente.settore}")
            print(f"      Email: {cliente.email}")
            print(f"      Messaggi scambiati: {cliente.numero_messaggi}")
            print(f"      Stato: {cliente.stato}")
    
    # ===== FAQ =====
    print("\n\n❓ FAQ:")
    print("-"*70)
    faq_list = db.query(FAQDB).all()
    
    if not faq_list:
        print("   (Nessuna FAQ ancora)")
    else:
        print(f"   Totale: {len(faq_list)}")
        for faq in faq_list:
            print(f"\n   ❓ {faq.domanda_completa}")
            print(f"      Keywords: {faq.domanda_keywords}")
            print(f"      Settore: {faq.settore if faq.settore else 'Tutti'}")
            print(f"      Priorità: {faq.priorita}/10")
    
    # ===== MESSAGGI =====
    print("\n\n💬 MESSAGGI (ultimi 5):")
    print("-"*70)
    messaggi = db.query(MessaggioDB).order_by(MessaggioDB.id.desc()).limit(5).all()
    
    if not messaggi:
        print("   (Nessun messaggio ancora)")
    else:
        for msg in messaggi:
            print(f"\n   📨 {msg.cliente_phone}")
            print(f"      Cliente: {msg.testo_cliente[:50]}...")
            print(f"      Risposta: {msg.testo_risposta[:50]}...")
            print(f"      Tipo: {msg.tipo_risposta}")
    
    print("\n" + "="*70)
    print("✅ Fine visualizzazione")
    print("="*70 + "\n")
    
    db.close()

if __name__ == "__main__":
    visualizza_database()
