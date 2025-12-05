"""
Modello Cliente - Rappresenta un cliente WhatsApp
"""

# Per adesso usiamo SQLite semplice, domani migrerai su PostgreSQL

import json
from datetime import datetime

class Cliente:
    """Classe che rappresenta un cliente"""
    
    # Questa è una lista in memoria (adesso)
    # Domani diventerà un database vero
    _clienti_database = []
    _id_counter = 1
    
    def __init__(self, phone, nome="", azienda="", settore="generico", email=""):
        self.id = Cliente._id_counter
        Cliente._id_counter += 1
        
        self.phone = phone  # es: "+393331234567"
        self.nome = nome
        self.azienda = azienda
        self.settore = settore  # "finanza", "sport", "coworking", "generico"
        self.email = email
        self.etichette = []  # es: ["VIP", "Attivo"]
        self.note = ""
        self.data_creazione = datetime.utcnow()
        self.ultima_interazione = datetime.utcnow()
        self.numero_messaggi = 0
        self.stato = "attivo"  # "attivo", "inattivo", "blocked"
    
    def save(self):
        """Salva il cliente nella memoria (database mock)"""
        Cliente._clienti_database.append(self)
        return self
    
    @staticmethod
    def trova_per_phone(phone):
        """Cerca cliente per numero telefono"""
        for cliente in Cliente._clienti_database:
            if cliente.phone == phone:
                return cliente
        return None
    
    @staticmethod
    def tutti():
        """Ritorna tutti i clienti"""
        return Cliente._clienti_database
    
    def to_dict(self):
        """Converti cliente in dizionario (per JSON)"""
        return {
            'id': self.id,
            'phone': self.phone,
            'nome': self.nome,
            'azienda': self.azienda,
            'settore': self.settore,
            'email': self.email,
            'etichette': self.etichette,
            'numero_messaggi': self.numero_messaggi,
            'stato': self.stato
        }
    
    def __repr__(self):
        return f"<Cliente {self.nome} - {self.phone}>"

# CLIENTI DI ESEMPIO (per testare)
# Aggiungeremo questi quando il bot parte
CLIENTI_INIZIALI = [
    {
        'phone': '+393331234567',
        'nome': 'Mario Rossi',
        'azienda': 'Rossi & Co',
        'settore': 'finanza',
        'email': 'mario@rossi.it'
    },
    {
        'phone': '+393339876543',
        'nome': 'Giulia Bianchi',
        'azienda': 'Sport Club',
        'settore': 'sport',
        'email': 'giulia@sportclub.it'
    }
]

# Carica clienti iniziali
for dati in CLIENTI_INIZIALI:
    cliente = Cliente(**dati)
    cliente.save()

print(f"✅ {len(Cliente.tutti())} clienti di test caricati")
