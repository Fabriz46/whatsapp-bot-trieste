"""
Script per aggiungere FAQ complete per tutti i settori
"""

import sys
sys.path.insert(0, '.')

from database import get_db_session, FAQDB
from datetime import datetime

def aggiungi_faq_complete():
    """Aggiunge 25+ FAQ per tutti i settori"""
    
    db = get_db_session()
    
    print("\n" + "="*70)
    print("➕ AGGIUNTA FAQ COMPLETE")
    print("="*70 + "\n")
    
    # FAQ GENERICHE (per tutti)
    faq_generiche = [
        {
            "domanda_keywords": "orari,apertura,quando,disponibilità,aperto,orario,siete aperti",
            "domanda_completa": "A che ora siete aperti?",
            "risposta": """📍 ORARI TRIESTE:
🕐 Lunedì-Venerdì: 9:00-18:00
🕐 Sabato: 9:00-13:00
🕐 Domenica: Chiuso

Per emergenze: disponibili su richiesta""",
            "settore": "",
            "priorita": 10
        },
        {
            "domanda_keywords": "contatto,numero,telefono,mail,email,dove,indirizzo,posizione,posizionati",
            "domanda_completa": "Come posso contattarvi?",
            "risposta": """📞 CONTATTI TRIESTE:

☎️ Telefono: +39 040 123456
📧 Email: info@trieste-facility.it
📍 Via Mezzo, 15 - Trieste
🌐 www.trieste-facility.it
📱 WhatsApp: QUESTO NUMERO
⏰ Orari risposta: Lun-Ven 9-18""",
            "settore": "",
            "priorita": 10
        },
        {
            "domanda_keywords": "prezzi,costo,quanto,tariffa,listino,price,tariffe,fee",
            "domanda_completa": "Quali sono i vostri prezzi?",
            "risposta": """💰 TARIFFE GENERALI:

Contattaci direttamente per:
- Offerta personalizzata
- Sconti per clienti fedeli
- Pacchetti annuali
- Accordi corporate

📞 +39 040 123456
📧 info@trieste-facility.it""",
            "settore": "",
            "priorita": 9
        },
        {
            "domanda_keywords": "chi siete,chi sei,azienda,società,informazioni,storia,background",
            "domanda_completa": "Chi siete? Raccontatemi di voi",
            "risposta": """🏢 CHI SIAMO:

Siamo una facility sportiva e di servizi a Trieste.
Offriamo:
✅ Coaching sportivo professionale
✅ Spazi di co-working
✅ Servizi di assicurazione e protezione
✅ Consulenza finanziaria

📊 Esperienza: +10 anni nel settore
👥 Clienti soddisfatti: 500+

Scopri di più: www.trieste-facility.it""",
            "settore": "",
            "priorita": 7
        },
    ]
    
    # FAQ SPORT
    faq_sport = [
        {
            "domanda_keywords": "prenotare,prenoto,booking,disponibilità,libero,campo,slot,ora",
            "domanda_completa": "Come prenoto un campo padel?",
            "risposta": """🏓 PRENOTAZIONE PADEL:

1️⃣ Scrivi qui su WhatsApp
2️⃣ Dimmi giorno e ora preferiti
3️⃣ Noi confermiamo disponibilità
4️⃣ Paghi in loco (contanti/carta)

⏰ DISPONIBILITÀ:
   Lun-Dom: 9:00-20:00
   Con almeno 2h di anticipo

💰 Tariffe: €25/ora singolo""",
            "settore": "sport",
            "priorita": 10
        },
        {
            "domanda_keywords": "lezione,allenamento,training,coaching,istruttore,allenare,imparare",
            "domanda_completa": "Offrite lezioni di tennis o padel?",
            "risposta": """🎾 LEZIONI SPORT:

✅ PADEL: Tutti i livelli
✅ TENNIS: Principianti e intermedi
✅ PERSONAL TRAINING: 1-to-1 con istruttore

📅 Frequenza: Settimanale / Intensiva
👨‍🏫 Istruttori certificati
📊 Valutazione personalizzata

Contatta: +39 040 123456""",
            "settore": "sport",
            "priorita": 9
        },
        {
            "domanda_keywords": "attrezzatura,racchetta,palla,equipaggiamento,noleggio,affitto",
            "domanda_completa": "Che attrezzatura devo portare?",
            "risposta": """🎾 ATTREZZATURA:

✅ NOLEGGIO DISPONIBILE:
   - Racchette: €5/ora
   - Scarpe: €3/ora
   - Palle: incluse nella tariffa

📋 RACCHETTE CONSIGLIATE:
   - Padel: 330-365g
   - Tennis: 280-320g

ℹ️ Consiglio: Portate le vostre per miglior comfort""",
            "settore": "sport",
            "priorita": 8
        },
        {
            "domanda_keywords": "abbonamento,pacchetto,bundle,mensile,trimestrale,annuale",
            "domanda_completa": "Avete abbonamenti o pacchetti?",
            "risposta": """💳 ABBONAMENTI & PACCHETTI:

📦 PADEL:
   • 10 ore: €200 (€20/ora)
   • 20 ore: €350 (€17.50/ora)
   • Mensile illimitato: €400

📦 LEZIONI:
   • 4 lezioni: €120
   • 8 lezioni: €220
   • Mensile illimitato: €350

🎁 SCONTO FEDELTÀ: 10% per clienti 6+ mesi""",
            "settore": "sport",
            "priorita": 9
        },
    ]
    
    # FAQ COWORKING
    faq_coworking = [
        {
            "domanda_keywords": "spazi,sale,riunioni,meeting,conferenza,workshop,evento,saletta",
            "domanda_completa": "Avete spazi per riunioni o eventi?",
            "risposta": """📋 SPAZI RIUNIONI:

✅ Sala Trieste (20 persone)
✅ Sala Meeting (10 persone)
✅ Area Lounge (informale)

🖥️ SERVIZI INCLUSI:
   • WiFi 1Gbps
   • Proiettore 4K
   • Tavoli/sedie ergonomiche
   • Parcheggio gratuito
   • Catering opzionale

📞 Richiedi preventivo: +39 040 123456""",
            "settore": "coworking",
            "priorita": 10
        },
        {
            "domanda_keywords": "scrivania,desk,posto,lavoro,ufficio,fisso,giornaliero,mensile",
            "domanda_completa": "Quali scrivanie/posti offrite?",
            "risposta": """💼 POSTI DI LAVORO:

🏢 SCRIVANIE FISSE:
   Accesso 24/7, tutto incluso
   • Mensile: €400
   • Trimestrale: €1.050 (sconto 12.5%)

🪑 POSTAZIONI GIORNALIERE:
   • Giorno: €20
   • 5 giorni: €90

☕ HOT DESK:
   Condiviso, flessibile
   • Giorno: €15
   • Mensile: €250""",
            "settore": "coworking",
            "priorita": 9
        },
        {
            "domanda_keywords": "wifi,internet,velocità,connessione,banda,fibra,tecnologia",
            "domanda_completa": "Com'è la connessione internet?",
            "risposta": """🌐 CONNESSIONE INTERNET:

✅ FIBRA OTTICA 1Gbps
✅ WiFi 6 (802.11ax)
✅ Backup 4G LTE

📊 VELOCITÀ GARANTITA:
   Download: 950 Mbps
   Upload: 450 Mbps
   Latenza: <5ms

🔒 SICUREZZA:
   VPN inclusa
   Firewall enterprise
   Backup automatico disponibile""",
            "settore": "coworking",
            "priorita": 8
        },
    ]
    
    # FAQ FINANZA/ASSICURAZIONE
    faq_finanza = [
        {
            "domanda_keywords": "assicurazione,polizza,protezione,copertura,rischio,danno,tutela",
            "domanda_completa": "Quali polizze assicurative offrite?",
            "risposta": """🛡️ POLIZZE ASSICURATIVE:

✅ RESPONSABILITÀ CIVILE
✅ PROTEZIONE PATRIMONIO
✅ COPERTURA INFORTUNI
✅ VITA & PREVIDENZA

📊 SOLUZIONI PERSONALIZZATE:
   • Per privati
   • Per professionisti
   • Per aziende
   • Per startup

📞 Consulenza GRATUITA: +39 040 123456""",
            "settore": "finanza",
            "priorita": 10
        },
        {
            "domanda_keywords": "consulenza,advisor,consiglio,pianificazione,investimento,portfolio",
            "domanda_completa": "Offrite consulenza finanziaria?",
            "risposta": """💰 CONSULENZA FINANZIARIA:

📈 SERVIZI:
   ✅ Pianificazione patrimoniale
   ✅ Strategie investimento
   ✅ Ottimizzazione fiscale
   ✅ Previdenza complementare

👨‍💼 CONSULENTI CERTIFICATI:
   • CFP (Certified Financial Planner)
   • Esperienza 10+ anni
   • Approccio personalizzato

🎯 PRIMA CONSULTAZIONE: GRATUITA

📞 Prenota: +39 040 123456""",
            "settore": "finanza",
            "priorita": 9
        },
    ]

        # FAQ AGGIUNTIVE SPORT (continua la lista)
    faq_sport_extra = [
        {
            "domanda_keywords": "gruppo,squadra,team,torneo,competizione,gara,campionato",
            "domanda_completa": "Organizzate tornei o competizioni?",
            "risposta": """🏆 TORNEI & COMPETIZIONI:

✅ TORNEO PADEL MENSILE
   • Open level
   • Premi in palio
   • Prossima edizione: 15 Gennaio

✅ CAMPIONATO TENNIS ANNUALE
   • 3 categorie (A, B, C)
   • Iscrizioni aperte
   • Final 8 a marzo

📞 Info e iscrizioni: +39 040 123456""",
            "settore": "sport",
            "priorita": 8
        },
        {
            "domanda_keywords": "social,instagram,facebook,seguire,community,news,aggiornamenti",
            "domanda_completa": "Come vi seguo sui social?",
            "risposta": """📱 SEGUICI SUI SOCIAL:

📸 Instagram: @trieste_facility
👍 Facebook: Trieste Facility
🎥 TikTok: @trieste_facility_padel
🎙️ Podcast: Trieste Sports Talk

📢 RICEVI AGGIORNAMENTI:
   • Offerte esclusive
   • Eventi speciali
   • Risultati tornei
   • Tips & trick

Segui adesso! 🔔""",
            "settore": "sport",
            "priorita": 7
        },
    ]
    
    # FAQ AGGIUNTIVE COWORKING
    faq_coworking_extra = [
        {
            "domanda_keywords": "parcheggio,auto,macchina,parking,gratuito,a pagamento,disponibilità",
            "domanda_completa": "C'è parcheggio disponibile?",
            "risposta": """🅿️ PARCHEGGIO:

✅ GRATUITO per:
   • Membri coworking
   • Clienti riunioni
   • Visitatori (2h gratuite)

📍 DISPONIBILITÀ:
   • 30 posti in loco
   • 10 posti sotterranei
   • 5 posti disabili

⚠️ Consiglio: Arriva 15min prima nei weekend""",
            "settore": "coworking",
            "priorita": 8
        },
        {
            "domanda_keywords": "catering,cibo,caffè,bar,snack,pranzo,bevande,mensa",
            "domanda_completa": "Offrite catering o bar?",
            "risposta": """☕ CATERING & BEVANDE:

✅ BARRE CAFFÈ:
   • Espresso, cappuccino, etc
   • Tisane, succhi
   • €1-3 per bevanda

✅ SNACK & PIZZA:
   • Al taglio disponibile
   • Insalate fresche
   • Panini gourmet

📦 CATERING RIUNIONI:
   • Pacchetti personalizzati
   • Min 10 persone
   • Prenota 2 giorni prima

📞 Menu: info@trieste-facility.it""",
            "settore": "coworking",
            "priorita": 7
        },
        {
            "domanda_keywords": "reception,supporto,help,assistenza,staff,aiuto,servizio,concierge",
            "domanda_completa": "Avete reception o support?",
            "risposta": """👥 RECEPTION & SUPPORT:

✅ RECEPTION 24/7:
   • Accoglienza ospiti
   • Gestione posti auto
   • Info generali

✅ SUPPORTO TECNICO:
   • WiFi/Internet: sempre disponibile
   • Assistenza computer
   • Printer/scanner support

✅ CONCIERGE:
   • Prenotazioni taxi/hotel
   • Spedizioni
   • Assistenza varia

📞 Reception: +39 040 123456 (interno 0)""",
            "settore": "coworking",
            "priorita": 8
        },
    ]
    
    # FAQ AGGIUNTIVE FINANZA
    faq_finanza_extra = [
        {
            "domanda_keywords": "costo,commissione,fee,tariffe,quanto,prezzo,gratuito,gratis",
            "domanda_completa": "Qual è il costo della consulenza?",
            "risposta": """💰 TARIFFE CONSULENZA:

✅ PRIMA CONSULENZA: GRATUITA
   (1 ora, valutazione iniziale)

✅ PIANO MENSILE:
   • €150/mese (1 ora/mese)
   • €300/mese (2 ore/mese)
   • €500/mese (4 ore/mese)

✅ PIANI ANNUALI:
   • Sconto 10% su tariffe mensili

✅ CORPORATE:
   • Tariffe dedicate
   • Team training incluso

📞 Richiedi preventivo: +39 040 123456""",
            "settore": "finanza",
            "priorita": 8
        },
        {
            "domanda_keywords": "documento,contratto,carta,firma,sottoscrizione,polizza,documenti",
            "domanda_completa": "Quali documenti mi servono?",
            "risposta": """📋 DOCUMENTI NECESSARI:

PER CONSULENZA FINANZA:
   ✅ ID (Carta identità/Passaporto)
   ✅ Codice fiscale
   ✅ Ultimi dichiarazioni redditi
   ✅ Estratti conti (opzionale)

PER ASSICURAZIONE:
   ✅ Dati anagrafici completi
   ✅ Beneficiari (se polizza vita)
   ✅ Stato di salute dichiarazione

📧 Mandaci i documenti via email protetta
📞 Info: info@trieste-facility.it""",
            "settore": "finanza",
            "priorita": 7
        },
        {
            "domanda_keywords": "riservatezza,privacy,dati,confidenziale,protezione,gdpr,sicurezza",
            "domanda_completa": "Come proteggete i miei dati?",
            "risposta": """🔒 PRIVACY & SICUREZZA:

✅ CONFORMITÀ GDPR
   • Dati crittografati
   • Accesso limitato staff
   • No sharing terze parti

✅ CONSULTORI CERTIFICATI:
   • Segreto professionale
   • Assicurazione responsabilità
   • Competenza legale

✅ ARCHIVI BLINDATI:
   • Backup automatici
   • Disaster recovery
   • Audit annuali

📜 Leggi la privacy policy completa:
www.trieste-facility.it/privacy""",
            "settore": "finanza",
            "priorita": 8
        },
    ]
    
    # Unisci tutte
    tutte_faq = faq_generiche + faq_sport + faq_coworking + faq_finanza + faq_sport_extra + faq_coworking_extra + faq_finanza_extra
    
    aggiunte = 0
    
    for faq_data in tutte_faq:
        # Controlla se esiste già
        esistente = db.query(FAQDB).filter(
            FAQDB.domanda_completa == faq_data["domanda_completa"]
        ).first()
        
        if esistente:
            print(f"⏭️  FAQ esistente: {faq_data['domanda_completa'][:40]}...")
            continue
        
        # Crea nuova FAQ
        faq = FAQDB(
            domanda_keywords=faq_data["domanda_keywords"],
            domanda_completa=faq_data["domanda_completa"],
            risposta=faq_data["risposta"],
            settore=faq_data["settore"],
            priorita=faq_data["priorita"],
            data_creazione=datetime.utcnow()
        )
        
        db.add(faq)
        aggiunte += 1
        
        settore_label = faq_data["settore"] if faq_data["settore"] else "GENERICA"
        print(f"✅ [{settore_label}] {faq_data['domanda_completa'][:50]}...")
    
    db.commit()
    db.close()
    
    print("\n" + "="*70)
    print(f"✅ {aggiunte} FAQ nuove aggiunte!")
    print("="*70 + "\n")

if __name__ == "__main__":
    aggiungi_faq_complete()