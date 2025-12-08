"""
Integrazioni - Google Sheets, Email, Webhooks
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
from database import get_db_session, ClienteDB
from datetime import datetime
import requests

# ============================================================================
# EMAIL NOTIFICATIONS
# ============================================================================

def invia_email(destinatario, oggetto, corpo_html, corpo_testo=""):
    """
    Invia email tramite SMTP
    """
    
    # Se non configurato, simula l'invio
    if not Config.SMTP_SERVER:
        print(f"📧 [SIMULATO] Email a {destinatario}: {oggetto}")
        return True
    
    try:
        # Crea messaggio
        msg = MIMEMultipart('alternative')
        msg['Subject'] = oggetto
        msg['From'] = Config.SMTP_FROM
        msg['To'] = destinatario
        
        # Aggiungi corpo
        if corpo_testo:
            msg.attach(MIMEText(corpo_testo, 'plain'))
        msg.attach(MIMEText(corpo_html, 'html'))
        
        # Connetti e invia
        with smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.sendmail(Config.SMTP_FROM, [destinatario], msg.as_string())
        
        print(f"✅ Email inviata a {destinatario}")
        return True
    
    except Exception as e:
        print(f"❌ Errore email: {e}")
        return False


def notifica_admin_nuovo_cliente(cliente):
    """Notifica admin di nuovo cliente"""
    
    corpo_html = f"""
    <html>
        <body style="font-family: Arial; background: #f5f5f5; padding: 20px;">
            <div style="background: white; padding: 20px; border-radius: 8px;">
                <h2 style="color: #208089;">🎉 Nuovo Cliente!</h2>
                <p><strong>Nome:</strong> {cliente.nome}</p>
                <p><strong>Phone:</strong> {cliente.phone}</p>
                <p><strong>Azienda:</strong> {cliente.azienda or 'N/A'}</p>
                <p><strong>Settore:</strong> {cliente.settore}</p>
                <p><strong>Email:</strong> {cliente.email or 'N/A'}</p>
                <hr>
                <p style="color: #888; font-size: 12px;">
                    Bot WhatsApp Trieste - {datetime.now().strftime('%d/%m/%Y %H:%M')}
                </p>
            </div>
        </body>
    </html>
    """
    
    invia_email(
        Config.ADMIN_EMAIL,
        f"🎉 Nuovo cliente: {cliente.nome}",
        corpo_html
    )


def notifica_admin_errore_api(errore_tipo, dettagli):
    """Notifica admin di errore API critico"""
    
    corpo_html = f"""
    <html>
        <body style="font-family: Arial; background: #fff5f5; padding: 20px;">
            <div style="background: #ffe6e6; padding: 20px; border-radius: 8px; border-left: 4px solid #dc3545;">
                <h2 style="color: #dc3545;">⚠️ ERRORE API!</h2>
                <p><strong>Tipo:</strong> {errore_tipo}</p>
                <p><strong>Dettagli:</strong> {dettagli}</p>
                <p><strong>Timestamp:</strong> {datetime.now().isoformat()}</p>
                <hr>
                <p style="color: #888; font-size: 12px;">
                    Controlla i log su Railway per dettagli.
                </p>
            </div>
        </body>
    </html>
    """
    
    invia_email(
        Config.ADMIN_EMAIL,
        f"⚠️ ERRORE BOT: {errore_tipo}",
        corpo_html
    )


# ============================================================================
# WEBHOOK CALLBACKS
# ============================================================================

def invia_webhook_evento(evento_tipo, dati):
    """
    Invia evento a webhook esterno
    Utile per integrazioni con altri sistemi
    """
    
    if not hasattr(Config, 'WEBHOOK_URL') or not Config.WEBHOOK_URL:
        return False
    
    try:
        payload = {
            "timestamp": datetime.now().isoformat(),
            "tipo": evento_tipo,
            "dati": dati
        }
        
        response = requests.post(
            Config.WEBHOOK_URL,
            json=payload,
            timeout=5,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"✅ Webhook evento '{evento_tipo}' inviato")
            return True
        else:
            print(f"❌ Webhook fallito: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Errore webhook: {e}")
        return False


# ============================================================================
# GOOGLE SHEETS SYNC (Opzionale)
# ============================================================================

def sync_clienti_a_google_sheets():
    """
    Sincronizza clienti a Google Sheets
    (Richiede credenziali Google Service Account)
    """
    
    # Questa funzione richiede configurazione manuale
    # Per ora, salvimo i dati in CSV che può essere caricato manualmente
    
    print("📊 Sync a Google Sheets: richiede configurazione manuale")
    print("   Opzione: Exporta CSV e importa manualmente a Google Sheets")
    return False


# ============================================================================
# REPORT EMAIL SETTIMANALE
# ============================================================================

def invia_report_settimanale():
    """Invia report settimanale all'admin"""
    
    db = get_db_session()
    
    try:
        # Raccogli dati
        tot_clienti = db.query(ClienteDB).count()
        clienti_attivi = db.query(ClienteDB).filter(
            ClienteDB.stato == 'attivo'
        ).count()
        
        # Nuovi clienti questa settimana
        from datetime import timedelta
        una_settimana_fa = datetime.utcnow() - timedelta(days=7)
        nuovi_clienti = db.query(ClienteDB).filter(
            ClienteDB.data_creazione >= una_settimana_fa
        ).count()
        
        corpo_html = f"""
        <html>
            <body style="font-family: Arial; background: #f5f5f5; padding: 20px;">
                <div style="background: white; padding: 20px; border-radius: 8px;">
                    <h2 style="color: #208089;">📊 Report Settimanale</h2>
                    
                    <h3>Statistiche Clienti</h3>
                    <ul>
                        <li><strong>Totali:</strong> {tot_clienti}</li>
                        <li><strong>Attivi:</strong> {clienti_attivi}</li>
                        <li><strong>Nuovi questa settimana:</strong> {nuovi_clienti}</li>
                    </ul>
                    
                    <hr>
                    <p style="color: #888; font-size: 12px;">
                        Report generato: {datetime.now().strftime('%d/%m/%Y %H:%M')}
                    </p>
                </div>
            </body>
        </html>
        """
        
        invia_email(
            Config.ADMIN_EMAIL,
            "📊 Report Settimanale Bot WhatsApp",
            corpo_html
        )
    
    finally:
        db.close()
