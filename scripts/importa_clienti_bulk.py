"""
Script per importare clienti in bulk da CSV
Supporta grandi quantità di dati
"""

import sys
sys.path.insert(0, '.')

import csv
from database import get_db_session, ClienteDB
from datetime import datetime

def importa_clienti_da_csv(file_path, settore_default="generico"):
    """
    Importa clienti da CSV
    
    Formato CSV atteso:
    phone,nome,azienda,settore,email,etichette,note
    """
    
    db = get_db_session()
    
    clienti_aggiunti = 0
    clienti_duplicati = 0
    errori = []
    
    print("\n" + "="*70)
    print(f"📥 IMPORTAZIONE BULK DA CSV")
    print(f"   File: {file_path}")
    print("="*70 + "\n")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            if not reader.fieldnames:
                print("❌ File CSV vuoto o malformato")
                return
            
            print(f"📋 Colonne trovate: {', '.join(reader.fieldnames)}\n")
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (riga 1 è header)
                try:
                    phone = row.get('phone', '').strip()
                    
                    # Valida il numero
                    if not phone:
                        errori.append(f"Riga {row_num}: numero vuoto")
                        continue
                    
                    # Normalizza il numero (aggiungi + se manca)
                    if not phone.startswith("+"):
                        phone = "+" + phone
                    
                    # Controlla se esiste già
                    cliente_esistente = db.query(ClienteDB).filter(
                        ClienteDB.phone == phone
                    ).first()
                    
                    if cliente_esistente:
                        clienti_duplicati += 1
                        print(f"⏭️  Riga {row_num}: {phone} - {row.get('nome', 'N/A')} (GIÀ PRESENTE)")
                        continue
                    
                    # Crea nuovo cliente
                    cliente = ClienteDB(
                        phone=phone,
                        nome=row.get('nome', 'N/A'),
                        azienda=row.get('azienda', ''),
                        settore=row.get('settore', settore_default),
                        email=row.get('email', ''),
                        etichette=row.get('etichette', ''),
                        note=row.get('note', ''),
                        data_creazione=datetime.utcnow(),
                        ultima_interazione=datetime.utcnow(),
                        numero_messaggi=0,
                        stato="attivo"
                    )
                    
                    db.add(cliente)
                    clienti_aggiunti += 1
                    
                    print(f"✅ Riga {row_num}: {phone} - {row.get('nome', 'N/A')}")
                
                except Exception as e:
                    errori.append(f"Riga {row_num}: {str(e)}")
                    print(f"❌ Riga {row_num}: ERRORE - {str(e)}")
            
            # Commit tutti i clienti
            db.commit()
        
        # Statistiche finali
        print("\n" + "="*70)
        print("✅ IMPORTAZIONE COMPLETATA")
        print("="*70)
        print(f"   ✅ Clienti aggiunti: {clienti_aggiunti}")
        print(f"   ⏭️  Clienti duplicati (non aggiunti): {clienti_duplicati}")
        print(f"   ❌ Errori: {len(errori)}")
        
        if errori:
            print(f"\n⚠️  ERRORI DURANTE L'IMPORTAZIONE:")
            for errore in errori[:10]:  # Mostra primi 10 errori
                print(f"   - {errore}")
            if len(errori) > 10:
                print(f"   ... e {len(errori) - 10} altri errori")
        
        print("="*70 + "\n")
    
    except FileNotFoundError:
        print(f"❌ File '{file_path}' non trovato")
    except Exception as e:
        print(f"❌ Errore generale: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/importa_clienti_bulk.py <file.csv> [settore_default]")
        print("\nEsempio:")
        print("  python scripts/importa_clienti_bulk.py clienti.csv")
        print("  python scripts/importa_clienti_bulk.py clienti.csv finanza")
        sys.exit(1)
    
    file_csv = sys.argv[1]
    settore = sys.argv[2] if len(sys.argv) > 2 else "generico"
    
    importa_clienti_da_csv(file_csv, settore)
