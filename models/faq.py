"""
Modello FAQ - Rappresenta una domanda frequente
"""

class FAQ:
    """Classe che rappresenta una FAQ"""
    
    _faq_database = []
    _id_counter = 1
    
    def __init__(self, domanda_keywords, domanda_completa, risposta, settore="", priorita=5):
        self.id = FAQ._id_counter
        FAQ._id_counter += 1
        
        self.domanda_keywords = domanda_keywords  # es: "orari,apertura,quando"
        self.domanda_completa = domanda_completa  # es: "A che ora siete aperti?"
        self.risposta = risposta  # La risposta completa
        self.settore = settore  # "" = tutti, "sport" = solo sport
        self.priorita = priorita  # 1-10, più alto = trova prima
    
    def save(self):
        """Salva FAQ nel database"""
        FAQ._faq_database.append(self)
        return self
    
    @staticmethod
    def tutti():
        """Ritorna tutte le FAQ"""
        return FAQ._faq_database
    
    @staticmethod
    def per_settore(settore):
        """Ritorna FAQ per un settore specifico"""
        result = []
        for faq in FAQ._faq_database:
            # Includi FAQ generiche (settore="") e quelle specifiche
            if faq.settore == "" or faq.settore == settore:
                result.append(faq)
        return result
    
    def to_dict(self):
        """Converti FAQ in dizionario"""
        return {
            'id': self.id,
            'domanda_completa': self.domanda_completa,
            'settore': self.settore,
            'priorita': self.priorita
        }
    
    def __repr__(self):
        return f"<FAQ {self.id}: {self.domanda_completa[:30]}...>"

# FAQ DI ESEMPIO
FAQ_INIZIALI = [
    FAQ(
        domanda_keywords="orari,apertura,quando,disponibilità,aperto",
        domanda_completa="A che ora siete aperti?",
        risposta="📍 Orari Trieste:\n🕐 Lunedì-Venerdì: 9:00-18:00\n🕐 Sabato: 9:00-13:00\n🕐 Domenica: Chiuso\n\nContatti: +39 040 123456",
        settore="",
        priorita=10
    ),
    FAQ(
        domanda_keywords="prezzi,costo,quanto,tariffa,listino,price",
        domanda_completa="Quanto costano i vostri servizi?",
        risposta="💰 Tariffe:\n\n💼 COWORKING:\n- Mensile: €200-400\n- Giornaliero: €20\n\n🏓 PADEL:\n- Ora singola: €25\n- Abbonamento 10 ore: €200\n\n📞 Per offerta personalizzata contattaci!",
        settore="",
        priorita=9
    ),
    FAQ(
        domanda_keywords="contatto,numero,telefono,mail,email,like,facebook",
        domanda_completa="Come posso contattarvi?",
        risposta="📞 Contatti:\n☎️ Telefono: +39 040 123456\n📧 Email: info@trieste-facility.it\n📍 Via Mezzo, 15 - Trieste\n🌐 www.trieste-facility.it\n📱 WhatsApp: questo numero!",
        settore="",
        priorita=8
    ),
    FAQ(
        domanda_keywords="disponibilità,libero,prenotare,booking,slot",
        domanda_completa="Come prenoto un campo?",
        risposta="🏓 PRENOTAZIONE PADEL:\n\n1️⃣ Scrivi qui su WhatsApp\n2️⃣ Dimmi giorno e ora\n3️⃣ Noi confermiamo disponibilità\n4️⃣ Paghi in loco (contanti/carta)\n\nOrari disponibili: Lunedì-Domenica 9-20",
        settore="sport",
        priorita=9
    ),
]

# Carica FAQ iniziali
for faq in FAQ_INIZIALI:
    faq.save()

print(f"✅ {len(FAQ.tutti())} FAQ caricate")
