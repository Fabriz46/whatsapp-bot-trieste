"""
Data Export - Esporta dati in CSV, PDF, Excel
"""

import csv
import json
from io import StringIO
from datetime import datetime
from database import get_db_session, ClienteDB, FAQDB, MessaggioDB
import os

# ============================================================================
# EXPORT CSV
# ============================================================================

def export_clienti_csv():
    """Esporta tutti i clienti in CSV"""
    
    db = get_db_session()
    
    try:
        clienti = db.query(ClienteDB).all()
        
        # Crea CSV in memoria
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'phone', 'nome', 'azienda', 'settore', 'email', 
            'etichette', 'note', 'numero_messaggi', 'stato', 
            'data_creazione', 'ultima_interazione'
        ])
        
        # Dati
        for c in clienti:
            writer.writerow([
                c.phone,
                c.nome,
                c.azienda or '',
                c.settore,
                c.email or '',
                c.etichette or '',
                c.note or '',
                c.numero_messaggi,
                c.stato,
                c.data_creazione.isoformat() if c.data_creazione else '',
                c.ultima_interazione.isoformat() if c.ultima_interazione else ''
            ])
        
        csv_content = output.getvalue()
        
        # Salva su file
        filename = f"export_clienti_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = f"exports/{filename}"
        
        os.makedirs('exports', exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        print(f"✅ Clienti esportati: {filepath}")
        print(f"   Righe: {len(clienti)}")
        
        return csv_content, filename
    
    finally:
        db.close()


def export_faq_csv():
    """Esporta tutte le FAQ in CSV"""
    
    db = get_db_session()
    
    try:
        faq_list = db.query(FAQDB).all()
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'domanda_completa', 'domanda_keywords', 'risposta', 
            'settore', 'priorita', 'data_creazione'
        ])
        
        # Dati
        for f in faq_list:
            writer.writerow([
                f.domanda_completa,
                f.domanda_keywords or '',
                f.risposta,
                f.settore or '',
                f.priorita,
                f.data_creazione.isoformat() if f.data_creazione else ''
            ])
        
        csv_content = output.getvalue()
        
        # Salva su file
        filename = f"export_faq_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = f"exports/{filename}"
        
        os.makedirs('exports', exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        print(f"✅ FAQ esportate: {filepath}")
        print(f"   Righe: {len(faq_list)}")
        
        return csv_content, filename
    
    finally:
        db.close()


def export_messaggi_csv():
    """Esporta tutti i messaggi in CSV"""
    
    db = get_db_session()
    
    try:
        messaggi = db.query(MessaggioDB).all()
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'cliente_phone', 'testo_cliente', 'testo_risposta', 
            'tipo_risposta', 'data_messaggio'
        ])
        
        # Dati
        for m in messaggi:
            writer.writerow([
                m.cliente_phone,
                m.testo_cliente or '',
                m.testo_risposta or '',
                m.tipo_risposta,
                m.data_messaggio.isoformat() if m.data_messaggio else ''
            ])
        
        csv_content = output.getvalue()
        
        # Salva su file
        filename = f"export_messaggi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = f"exports/{filename}"
        
        os.makedirs('exports', exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        print(f"✅ Messaggi esportati: {filepath}")
        print(f"   Righe: {len(messaggi)}")
        
        return csv_content, filename
    
    finally:
        db.close()


def export_backup_completo():
    """Esporta backup completo in JSON"""
    
    db = get_db_session()
    
    try:
        # Raccogli tutti i dati
        clienti = db.query(ClienteDB).all()
        faq_list = db.query(FAQDB).all()
        messaggi = db.query(MessaggioDB).all()
        
        backup = {
            "data_backup": datetime.now().isoformat(),
            "clienti": [
                {
                    "id": c.id,
                    "phone": c.phone,
                    "nome": c.nome,
                    "azienda": c.azienda,
                    "settore": c.settore,
                    "email": c.email,
                    "etichette": c.etichette,
                    "note": c.note,
                    "numero_messaggi": c.numero_messaggi,
                    "stato": c.stato,
                    "data_creazione": c.data_creazione.isoformat() if c.data_creazione else None,
                    "ultima_interazione": c.ultima_interazione.isoformat() if c.ultima_interazione else None,
                }
                for c in clienti
            ],
            "faq": [
                {
                    "id": f.id,
                    "domanda_completa": f.domanda_completa,
                    "domanda_keywords": f.domanda_keywords,
                    "risposta": f.risposta,
                    "settore": f.settore,
                    "priorita": f.priorita,
                    "data_creazione": f.data_creazione.isoformat() if f.data_creazione else None,
                }
                for f in faq_list
            ],
            "messaggi": [
                {
                    "id": m.id,
                    "cliente_phone": m.cliente_phone,
                    "testo_cliente": m.testo_cliente,
                    "testo_risposta": m.testo_risposta,
                    "tipo_risposta": m.tipo_risposta,
                    "data_messaggio": m.data_messaggio.isoformat() if m.data_messaggio else None,
                }
                for m in messaggi
            ]
        }
        
        # Salva su file
        filename = f"backup_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = f"backups/{filename}"
        
        os.makedirs('backups', exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(backup, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ BACKUP COMPLETO: {filepath}")
        print(f"   • Clienti: {len(clienti)}")
        print(f"   • FAQ: {len(faq_list)}")
        print(f"   • Messaggi: {len(messaggi)}")
        
        return backup, filename
    
    finally:
        db.close()

# ============================================================================
# IMPORT CSV
# ============================================================================

def import_clienti_da_csv(filepath):
    """Importa clienti da file CSV"""
    
    db = get_db_session()
    
    try:
        print(f"\n📥 Importazione clienti da: {filepath}")
        
        aggiunti = 0
        duplicati = 0
        errori = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    phone = row.get('phone', '').strip()
                    
                    if not phone:
                        errori.append(f"Riga {row_num}: phone vuoto")
                        continue
                    
                    if not phone.startswith('+'):
                        phone = '+' + phone
                    
                    # Controlla duplicati
                    esistente = db.query(ClienteDB).filter(
                        ClienteDB.phone == phone
                    ).first()
                    
                    if esistente:
                        duplicati += 1
                        continue
                    
                    # Crea cliente
                    cliente = ClienteDB(
                        phone=phone,
                        nome=row.get('nome', 'N/A'),
                        azienda=row.get('azienda', ''),
                        settore=row.get('settore', 'generico'),
                        email=row.get('email', ''),
                        etichette=row.get('etichette', ''),
                        note=row.get('note', ''),
                        numero_messaggi=int(row.get('numero_messaggi', 0)),
                        stato=row.get('stato', 'attivo')
                    )
                    
                    db.add(cliente)
                    aggiunti += 1
                    
                except Exception as e:
                    errori.append(f"Riga {row_num}: {str(e)}")
            
            db.commit()
        
        print(f"✅ Importazione completata")
        print(f"   • Aggiunti: {aggiunti}")
        print(f"   • Duplicati: {duplicati}")
        print(f"   • Errori: {len(errori)}")
        
        return aggiunti, duplicati, errori
    
    except Exception as e:
        print(f"❌ Errore importazione: {e}")
        return 0, 0, [str(e)]
    finally:
        db.close()


def import_faq_da_csv(filepath):
    """Importa FAQ da file CSV"""
    
    db = get_db_session()
    
    try:
        print(f"\n📥 Importazione FAQ da: {filepath}")
        
        aggiunti = 0
        duplicati = 0
        errori = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    domanda = row.get('domanda_completa', '').strip()
                    risposta = row.get('risposta', '').strip()
                    
                    if not domanda or not risposta:
                        errori.append(f"Riga {row_num}: domanda o risposta vuota")
                        continue
                    
                    # Controlla duplicati
                    esistente = db.query(FAQDB).filter(
                        FAQDB.domanda_completa == domanda
                    ).first()
                    
                    if esistente:
                        duplicati += 1
                        continue
                    
                    # Crea FAQ
                    faq = FAQDB(
                        domanda_completa=domanda,
                        domanda_keywords=row.get('domanda_keywords', ''),
                        risposta=risposta,
                        settore=row.get('settore', ''),
                        priorita=int(row.get('priorita', 5))
                    )
                    
                    db.add(faq)
                    aggiunti += 1
                    
                except Exception as e:
                    errori.append(f"Riga {row_num}: {str(e)}")
            
            db.commit()
        
        print(f"✅ Importazione completata")
        print(f"   • Aggiunti: {aggiunti}")
        print(f"   • Duplicati: {duplicati}")
        print(f"   • Errori: {len(errori)}")
        
        return aggiunti, duplicati, errori
    
    except Exception as e:
        print(f"❌ Errore importazione: {e}")
        return 0, 0, [str(e)]
    finally:
        db.close()
