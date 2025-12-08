"""
Analytics - Statistiche e report avanzati
"""

from database import get_db_session, ClienteDB, MessaggioDB, FAQDB
from datetime import datetime, timedelta
from collections import Counter
import statistics

# ============================================================================
# ANALYTICS AVANZATE
# ============================================================================

def get_analytics_dashboard():
    """Ritorna statistiche complete per dashboard"""
    
    db = get_db_session()
    
    try:
        # CLIENTI
        tot_clienti = db.query(ClienteDB).count()
        clienti_attivi = db.query(ClienteDB).filter(
            ClienteDB.stato == 'attivo'
        ).count()
        
        # Ultimi 7 giorni
        sette_giorni_fa = datetime.utcnow() - timedelta(days=7)
        nuovi_clienti_settimana = db.query(ClienteDB).filter(
            ClienteDB.data_creazione >= sette_giorni_fa
        ).count()
        
        # Ultimi 30 giorni
        trenta_giorni_fa = datetime.utcnow() - timedelta(days=30)
        clienti_inattivi = db.query(ClienteDB).filter(
            ClienteDB.ultima_interazione < trenta_giorni_fa
        ).count()
        
        # MESSAGGI
        tot_messaggi = db.query(MessaggioDB).count()
        messaggi_oggi = db.query(MessaggioDB).filter(
            MessaggioDB.data_messaggio >= datetime.combine(
                datetime.utcnow().date(),
                datetime.min.time()
            )
        ).count()
        
        messaggi_settimana = db.query(MessaggioDB).filter(
            MessaggioDB.data_messaggio >= sette_giorni_fa
        ).count()
        
        # Tipo di risposta (FAQ vs Perplexity)
        faq_count = db.query(MessaggioDB).filter(
            MessaggioDB.tipo_risposta == 'faq'
        ).count()
        perplexity_count = db.query(MessaggioDB).filter(
            MessaggioDB.tipo_risposta == 'perplexity'
        ).count()
        
        # FAQ
        tot_faq = db.query(FAQDB).count()
        
        # Settore clienti (distribuzione)
        settori = db.query(ClienteDB.settore, func.count(ClienteDB.id)).group_by(
            ClienteDB.settore
        ).all()
        
        # Media messaggi per cliente
        tutti_clienti = db.query(ClienteDB).all()
        if tutti_clienti:
            media_msg = statistics.mean([c.numero_messaggi for c in tutti_clienti])
        else:
            media_msg = 0
        
        return {
            "clienti": {
                "totali": tot_clienti,
                "attivi": clienti_attivi,
                "inattivi": clienti_inattivi,
                "nuovi_settimana": nuovi_clienti_settimana,
                "tasso_attivazione": round((clienti_attivi / tot_clienti * 100), 2) if tot_clienti > 0 else 0,
            },
            "messaggi": {
                "totali": tot_messaggi,
                "oggi": messaggi_oggi,
                "settimana": messaggi_settimana,
                "faq": faq_count,
                "perplexity": perplexity_count,
                "media_per_cliente": round(media_msg, 2),
            },
            "faq": {
                "totali": tot_faq,
            },
            "settori": {
                s[0] if s[0] else "generico": s[1]
                for s in settori
            },
            "timestamp": datetime.now().isoformat()
        }
    
    finally:
        db.close()


def get_report_giornaliero():
    """Report giornaliero"""
    
    db = get_db_session()
    
    try:
        oggi = datetime.utcnow().date()
        
        messaggi_oggi = db.query(MessaggioDB).filter(
            MessaggioDB.data_messaggio >= datetime.combine(oggi, datetime.min.time())
        ).all()
        
        nuovi_clienti = db.query(ClienteDB).filter(
            ClienteDB.data_creazione >= datetime.combine(oggi, datetime.min.time())
        ).all()
        
        return {
            "data": oggi.isoformat(),
            "messaggi_totali": len(messaggi_oggi),
            "nuovi_clienti": len(nuovi_clienti),
            "clienti": [c.nome for c in nuovi_clienti],
            "timestamp": datetime.now().isoformat()
        }
    
    finally:
        db.close()


def get_report_mensile():
    """Report mensile"""
    
    db = get_db_session()
    
    try:
        trenta_giorni_fa = datetime.utcnow() - timedelta(days=30)
        
        messaggi_mese = db.query(MessaggioDB).filter(
            MessaggioDB.data_messaggio >= trenta_giorni_fa
        ).count()
        
        nuovi_clienti_mese = db.query(ClienteDB).filter(
            ClienteDB.data_creazione >= trenta_giorni_fa
        ).count()
        
        clienti_attivi_mese = db.query(ClienteDB).filter(
            ClienteDB.ultima_interazione >= trenta_giorni_fa,
            ClienteDB.stato == 'attivo'
        ).count()
        
        return {
            "periodo": f"{(datetime.utcnow() - timedelta(days=30)).strftime('%d/%m/%Y')} - {datetime.utcnow().strftime('%d/%m/%Y')}",
            "messaggi": messaggi_mese,
            "nuovi_clienti": nuovi_clienti_mese,
            "clienti_attivi": clienti_attivi_mese,
            "timestamp": datetime.now().isoformat()
        }
    
    finally:
        db.close()


# Importa func per le query
from sqlalchemy import func
