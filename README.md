# 🤖 WhatsApp Bot Trieste - Sistema Completo

## Funzionalità

### ✅ Bot WhatsApp
- Webhook per ricevere messaggi
- Matching FAQ intelligente
- AI con Perplexity per risposte avanzate
- Logging completo

### ✅ Dashboard Interattiva
- Autenticazione (Login/Logout)
- Gestione Clienti (CRUD)
- Gestione FAQ (CRUD)
- Analytics real-time

### ✅ Automazioni
- Benvenuto nuovi clienti (ogni ora)
- Reminder settimanali (lunedì 9:00)
- Upsell intelligente (ogni 3 giorni)
- Notifiche admin (ogni 6 ore)
- Pulizia dati (domenica 2:00 AM)

### ✅ Integrazioni
- Export/Import CSV e JSON
- Email notifications
- Webhook callbacks
- Google Sheets (manuale)

### ✅ Analytics
- Dashboard statistiche
- Report giornaliero/mensile
- Analisi settori clienti
- Tracking risposta API

## Setup

\`\`\`bash
git clone <repo>
cd whatsapp-bot-trieste
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
\`\`\`

## Accesso

- **Login:** http://localhost:5000/login
- **Admin:** admin / trieste_bot_2025
- **Dashboard:** http://localhost:5000/dashboard

## Variabili d'Ambiente (.env)

\`\`\`
DATABASE_URL=postgresql://...
WHATSAPP_TOKEN=...
WHATSAPP_PHONE_ID=...
PERPLEXITY_API_KEY=pplx-sk-...
SMTP_SERVER=smtp.gmail.com
SMTP_USER=...
SMTP_PASSWORD=...
ADMIN_EMAIL=...
\`\`\`

## Deploy

Su Railway:
1. Connetti GitHub
2. Set variabili d'ambiente
3. Deploy automatico

---

Creato con ❤️ da David Iozzo
