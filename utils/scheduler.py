"""
Scheduler - Sistema di automazioni e task programmati
Usa APScheduler per eseguire job periodicamente
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from database import get_db_session, ClienteDB, MessaggioDB, UserDB
from routes.webhook import invia_messaggio_whatsapp
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

# ============================================================================
# TASK 1: BENVENUTO AL PRIMO MESSAGGIO
# ============================================================================

def task_benvenuto_nuovo_cliente():
    """
    Invia messaggio di benvenuto ai nuovi clienti
    (che non hanno ancora interagito)
    
    Eseguito: Ogni 1 ora
    """
    print("\n🤖 [TASK] Cercando nuovi clienti da salutare...")
    
    db = get_db_session()
    
    try:
        # Clienti creati nelle ultime 24 ore senza messaggi
        ieri = datetime.utcnow() - timedelta(days=1)
        
        nuovi_clienti = db.query(ClienteDB).filter(
            ClienteDB.data_creazione >= ieri,
            ClienteDB.numero_messaggi == 0
        ).all()
        
        if not nuovi_clienti:
            print("   ℹ️  Nessun nuovo cliente da salutare")
            return
        
        print(f"   ✅ Trovati {len(nuovi_clienti)} nuovi clienti")
        
        for cliente in nuovi_clienti:
            messaggio = f"""👋 Ciao {cliente.nome}!

Benvenuto in Trieste Facility! 🎾

Siamo qui per aiutarti con:
✅ Prenotazioni padel e tennis
✅ Consulenza sportiva personalizzata
✅ Servizi di protezione finanziaria
✅ Spazi di coworking

📞 Contattaci per qualsiasi domanda!"""
            
            try:
                invia_messaggio_whatsapp(cliente.phone, messaggio)
                print(f"   📨 Benvenuto inviato a {cliente.nome} ({cliente.phone})")
            except Exception as e:
                print(f"   ❌ Errore invio a {cliente.phone}: {e}")
    
    except Exception as e:
        print(f"   ❌ Errore task benvenuto: {e}")
    finally:
        db.close()


# ============================================================================
# TASK 2: REMINDER SETTIMANALE
# ============================================================================

def task_reminder_settimanale():
    """
    Invia reminder settimanale ai clienti attivi
    
    Eseguito: Ogni lunedì mattina alle 9:00
    """
    print("\n🤖 [TASK] Inviando reminder settimanali...")
    
    db = get_db_session()
    
    try:
        # Clienti attivi (ultimi 30 giorni)
        trenta_giorni_fa = datetime.utcnow() - timedelta(days=30)
        
        clienti_attivi = db.query(ClienteDB).filter(
            ClienteDB.stato == 'attivo',
            ClienteDB.ultima_interazione >= trenta_giorni_fa
        ).all()
        
        print(f"   ℹ️  Clienti attivi: {len(clienti_attivi)}")
        
        for cliente in clienti_attivi[:10]:  # Max 10 per volta
            messaggio = f"""📢 Ciao {cliente.nome}! 

Ricordati di noi questa settimana:

🏓 Padel: Prenotazioni aperte!
🎾 Tennis: Lezioni disponibili
💼 Coworking: 10% sconto per abbonati
💰 Protezione Finanziaria: Consulenza gratuita

📞 Rispondi per prenotare!"""
            
            try:
                invia_messaggio_whatsapp(cliente.phone, messaggio)
                print(f"   📨 Reminder inviato a {cliente.nome}")
            except Exception as e:
                print(f"   ❌ Errore: {e}")
    
    except Exception as e:
        print(f"   ❌ Errore task reminder: {e}")
    finally:
        db.close()


# ============================================================================
# TASK 3: UPSELL INTELLIGENTE
# ============================================================================

def task_upsell_intelligente():
    """
    Suggerisce servizi basati sulla storia e settore del cliente
    
    Eseguito: Ogni 3 giorni
    """
    print("\n🤖 [TASK] Analizzando clienti per upsell...")
    
    db = get_db_session()
    
    try:
        # Clienti che non hanno messaggi da 7 giorni
        una_settimana_fa = datetime.utcnow() - timedelta(days=7)
        
        clienti_inattivi = db.query(ClienteDB).filter(
            ClienteDB.stato == 'attivo',
            ClienteDB.ultima_interazione < una_settimana_fa,
            ClienteDB.numero_messaggi > 0  # Hanno interagito almeno una volta
        ).all()
        
        print(f"   ℹ️  Clienti inattivi da ricontattare: {len(clienti_inattivi)}")
        
        for cliente in clienti_inattivi[:5]:
            # Suggerimento basato su settore
            if cliente.settore == 'sport':
                messaggio = """⚽ Manca il padel? 

Questo mese offerta speciale:
- 5 partite = 100€ (sconto 20%)
- Lezione tecnica gratuita
- Torneo a premi il 20 dicembre

Prenoti? 🏓"""
            
            elif cliente.settore == 'coworking':
                messaggio = """💼 Esigenza spazi di lavoro?

OFFERTA ESCLUSIVA:
- Scrivania fissa: €350/mese (era €400)
- WiFi 1Gbps + Catering
- 2 meeting room gratis/mese

Interessato? 📞"""
            
            elif cliente.settore == 'finanza':
                messaggio = """💰 Protezione Finanziaria

Nuovo piano protezione:
✅ Copertura ampliata
✅ Premi ridotti 15%
✅ Consulenza personalizzata

Consulenza gratuita? 📋"""
            
            else:
                continue
            
            try:
                invia_messaggio_whatsapp(cliente.phone, messaggio)
                print(f"   📨 Upsell inviato a {cliente.nome} (settore: {cliente.settore})")
            except Exception as e:
                print(f"   ❌ Errore: {e}")
    
    except Exception as e:
        print(f"   ❌ Errore task upsell: {e}")
    finally:
        db.close()


# ============================================================================
# TASK 4: NOTIFICHE ADMIN
# ============================================================================

def task_notifiche_admin():
    """
    Notifica l'admin di attività importanti
    
    Eseguito: Ogni 6 ore
    """
    print("\n🤖 [TASK] Controllando attività importanti...")
    
    db = get_db_session()
    
    try:
        # Ultimi messaggi (ultimi 30 min)
        trenta_min_fa = datetime.utcnow() - timedelta(minutes=30)
        
        messaggi_recenti = db.query(MessaggioDB).filter(
            MessaggioDB.data_messaggio >= trenta_min_fa
        ).count()
        
        # Nuovi clienti (ultimi 30 min)
        nuovi_clienti = db.query(ClienteDB).filter(
            ClienteDB.data_creazione >= trenta_min_fa
        ).count()
        
        # Clienti inattivi da più di 30 giorni
        trenta_giorni_fa = datetime.utcnow() - timedelta(days=30)
        clienti_inattivi = db.query(ClienteDB).filter(
            ClienteDB.ultima_interazione < trenta_giorni_fa
        ).count()
        
        print(f"   📊 Statistiche ultime 30 min:")
        print(f"      • Messaggi: {messaggi_recenti}")
        print(f"      • Nuovi clienti: {nuovi_clienti}")
        print(f"      • Clienti inattivi: {clienti_inattivi}")
        
        if messaggi_recenti > 10 or nuovi_clienti > 5:
            print(f"   ⚠️  Attività elevata!")
    
    except Exception as e:
        print(f"   ❌ Errore task notifiche: {e}")
    finally:
        db.close()


# ============================================================================
# TASK 5: PULIZIA DATI
# ============================================================================

def task_pulizia_dati():
    """
    Pulizia periodica del database
    - Elimina messaggi più vecchi di 90 giorni
    - Archivia clienti inattivi
    
    Eseguito: Ogni domenica alle 2:00 AM
    """
    print("\n🤖 [TASK] Pulizia database...")
    
    db = get_db_session()
    
    try:
        # Elimina messaggi vecchi di 90 giorni
        novanta_giorni_fa = datetime.utcnow() - timedelta(days=90)
        
        messaggi_rimossi = db.query(MessaggioDB).filter(
            MessaggioDB.data_messaggio < novanta_giorni_fa
        ).delete()
        
        db.commit()
        
        print(f"   ✅ {messaggi_rimossi} messaggi vecchi eliminati")
    
    except Exception as e:
        print(f"   ❌ Errore task pulizia: {e}")
    finally:
        db.close()


# ============================================================================
# REGISTRAZIONE TASK
# ============================================================================

def registra_task():
    """Registra tutti i task nel scheduler"""
    
    print("\n" + "="*70)
    print("📅 REGISTRAZIONE TASK SCHEDULER")
    print("="*70)
    
    # Task 1: Benvenuto (ogni ora)
    scheduler.add_job(
        func=task_benvenuto_nuovo_cliente,
        trigger=CronTrigger(minute=0),  # Ogni ora
        id='benvenuto_nuovi_clienti',
        name='Benvenuto nuovi clienti',
        replace_existing=True
    )
    print("✅ Task 1: Benvenuto (ogni ora)")
    
    # Task 2: Reminder (lunedì 9:00)
    scheduler.add_job(
        func=task_reminder_settimanale,
        trigger=CronTrigger(day_of_week=0, hour=9, minute=0),  # Lunedì 9:00
        id='reminder_settimanale',
        name='Reminder settimanale',
        replace_existing=True
    )
    print("✅ Task 2: Reminder settimanale (lunedì 9:00)")
    
    # Task 3: Upsell (ogni 3 giorni)
    scheduler.add_job(
        func=task_upsell_intelligente,
        trigger=CronTrigger(hour=14, minute=0, day='*/3'),  # Ogni 3 giorni
        id='upsell_intelligente',
        name='Upsell intelligente',
        replace_existing=True
    )
    print("✅ Task 3: Upsell intelligente (ogni 3 giorni)")
    
    # Task 4: Notifiche admin (ogni 6 ore)
    scheduler.add_job(
        func=task_notifiche_admin,
        trigger=CronTrigger(hour='*/6', minute=0),  # Ogni 6 ore
        id='notifiche_admin',
        name='Notifiche admin',
        replace_existing=True
    )
    print("✅ Task 4: Notifiche admin (ogni 6 ore)")
    
    # Task 5: Pulizia dati (domenica 2:00)
    scheduler.add_job(
        func=task_pulizia_dati,
        trigger=CronTrigger(day_of_week=6, hour=2, minute=0),  # Domenica 2:00
        id='pulizia_dati',
        name='Pulizia dati',
        replace_existing=True
    )
    print("✅ Task 5: Pulizia dati (domenica 2:00 AM)")
    
    print("="*70 + "\n")


def start_scheduler():
    """Avvia lo scheduler"""
    if not scheduler.running:
        registra_task()
        scheduler.start()
        print("🟢 Scheduler avviato!\n")


def stop_scheduler():
    """Ferma lo scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        print("🔴 Scheduler fermato!\n")
