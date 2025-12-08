"""
Integrazioni - Google Sheets, Email, Webhooks
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
from database import get_db_session, ClienteDB
from datetime import datetime, timedelta
import requests

# --- IMPORT GOOGLE SHEETS ---
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ====================================================================
# EMAIL NOTIFICATIONS
# ====================================================================

def invia_email(destinatario, oggetto, corpo_html, corpo_testo=""):
    """
    Invia email tramite SMTP
    """

    # Se non configurato, simula l'invio
    if not Config.SMTP_SERVER:
        print(f"📧 [SIMULATO] Email a {destinatario}: {oggetto}")
        return True

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = oggetto
        msg['From'] = Config.SMTP_FROM
        msg['To'] = destinatario

        if corpo_testo:
            msg.attach(MIMEText(corpo_testo, 'plain'))

        msg.attach(MIMEText(corpo_html, 'html'))

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


# ====================================================================
# WEBHOOK CALLBACKS
# ====================================================================

def invia_webhook_evento(evento_tipo, dati):
    """
    Invia evento a webhook esterno
    """
    if not getattr(Config, "WEBHOOK_URL", None):
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

        print(f"❌ Webhook fallito: {response.status_code}")
        return False

    except Exception as e:
        print(f"❌ Errore webhook: {e}")
        return False


# ====================================================================
# GOOGLE SHEETS SYNC (IMPLEMENTATO)
# ====================================================================

def sync_clienti_a_google_sheets():
    """
    Legge la tabella clienti dal DB e la sincronizza nel Google Sheet.
    """

    print("\n📄 Avvio sincronizzazione Google Sheets...")

    json_path = Config.GOOGLE_SERVICE_ACCOUNT_JSON
    sheet_id = Config.GOOGLE_SHEETS_CLIENTI_ID

    # --- Controllo file JSON ---
    import os
    if not os.path.exists(json_path):
        print(f"❌ ERRORE: File credenziali non trovato: {json_path}")
        return False

    # --- Carica credenziali ---
    try:
        creds = service_account.Credentials.from_service_account_file(
            json_path,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
    except Exception as e:
        print("❌ Errore caricando il Service Account:", e)
        return False

    # --- Connessione Google Sheets ---
    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
    except Exception as e:
        print("❌ Errore collegando Google Sheets:", e)
        return False

    # --- Legge dal DB ---
    db = get_db_session()
    try:
        clienti = db.query(ClienteDB).order_by(ClienteDB.data_creazione.asc()).all()
    finally:
        db.close()

    # --- Prepara righe ---
    rows = [["ID", "Nome", "Cognome", "Telefono", "Email", "Stato", "Data Creazione"]]

    for c in clienti:
        rows.append([
            c.id,
            c.nome,
            c.cognome,
            c.phone,
            c.email,
            c.stato,
            c.data_creazione.strftime("%Y-%m-%d %H:%M")
        ])

    # --- CLEAR ---
    try:
        sheet.values().clear(
            spreadsheetId=sheet_id,
            range="A1:Z999"
        ).execute()
    except Exception as e:
        print("❌ Errore durante CLEAR del foglio:", e)
        return False

    # --- WRITE ---
    try:
        sheet.values().update(
            spreadsheetId=sheet_id,
            range="A1",
            valueInputOption="RAW",
            body={"values": rows}
        ).execute()
    except Exception as e:
        print("❌ Errore scrivendo sul foglio:", e)
        return False

    print(f"✅ Sincronizzazione completata: {len(clienti)} clienti esportati.")
    return True


# ====================================================================
# REPORT EMAIL SETTIMANALE
# ====================================================================

def invia_report_settimanale():
    """Invia report settimanale all'admin"""

    db = get_db_session()

    try:
        tot_clienti = db.query(ClienteDB).count()
        clienti_attivi = db.query(ClienteDB).filter(ClienteDB.stato == 'attivo').count()

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
