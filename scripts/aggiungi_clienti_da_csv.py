"""
Script per aggiungere clienti da CSV
"""

import csv
import sys

# Aggiungi la cartella padre al path per importare models
sys.path.insert(0, '.')

from models.cliente import Cliente

def importa_clienti(file_csv):
    """Legge CSV e aggiunge clienti"""
    
    print(f"\n📂 Apertura file: {file_csv}\n")
    
    clienti_aggiunti = 0
    clienti_duplicati = 0
    
    try:
        with open(file_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # Verifica se cliente esiste già
                if Cliente.trova_per_phone(row['phone']):
                    print(f"⏭️  {row['phone']} - {row['nome']} (GIÀ PRESENTE)")
                    clienti_duplicati += 1
                    continue
                
                # Crea nuovo cliente
                cliente = Cliente(
                    phone=row['phone'],
                    nome=row.get('nome', ''),
                    azienda=row.get('azienda', ''),
                    settore=row.get('settore', 'generico'),
                    email=row.get('email', '')
                )
                cliente.save()
                
                print(f"✅ {row['phone']} - {row['nome']}")
                clienti_aggiunti += 1
        
        print(f"\n" + "="*60)
        print(f"✅ IMPORTAZIONE COMPLETATA")
        print(f"   Clienti aggiunti: {clienti_aggiunti}")
        print(f"   Clienti duplicati (non aggiunti): {clienti_duplicati}")
        print(f"   Totale clienti nel DB: {len(Cliente.tutti())}")
        print(f"="*60 + "\n")
    
    except FileNotFoundError:
        print(f"\n❌ Errore: File '{file_csv}' non trovato!")
    except Exception as e:
        print(f"\n❌ Errore: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/aggiungi_clienti_da_csv.py <file.csv>")
        sys.exit(1)
    
    importa_clienti(sys.argv[1])
