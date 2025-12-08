"""
Integrazione con Perplexity API
"""

import requests
import os

def chiama_perplexity(messaggio_cliente, contesto_cliente=""):
    """
    Chiama Perplexity API per una risposta intelligente.
    
    Usato quando nessuna FAQ trova match.
    """
    
    # Prendi la key dal .env
    api_key = os.getenv("PERPLEXITY_API_KEY")
    
    # Se non hai key, torna risposta placeholder
    if not api_key or api_key == "":
        print("⚠️  PERPLEXITY_API_KEY non configurata")
        return """🤖 Grazie per la domanda! 

Per favore contattaci direttamente per una risposta personalizzata.
📞 +39 040 123456"""
    
    # Prepara il messaggio di sistema
    prompt_system = f"""Sei un assistente di supporto clienti per una facility sportiva a Trieste.

REGOLE:
- Rispondi SEMPRE in italiano
- Risposte brevi (max 80 parole)
- Professionali ma amichevoli
- Usa emoji quando appropriate

CONTESTO CLIENTE: {contesto_cliente}"""
    
    try:
        print("   🤖 Chiamo Perplexity API...")
        
        # Chiama API Perplexity
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar",
                "messages": [
                    {"role": "system", "content": prompt_system},
                    {"role": "user", "content": messaggio_cliente}
                ],
                "max_tokens": 200,
                "temperature": 0.7
            },
            timeout=10
        )
        
        # Controlla se la risposta è ok
        if response.status_code == 200:
            risposta = response.json()["choices"][0]["message"]["content"]
            print("   ✅ Risposta Perplexity ricevuta")
            return risposta
        else:
            print(f"   ❌ Errore Perplexity ({response.status_code})")
            return "⚠️  Errore temporaneo. Riprova tra poco."
    
    except requests.exceptions.Timeout:
        print("   ⏱️  Timeout - server lento")
        return "⏱️  Errore di timeout. Riprova tra poco."
    except Exception as e:
        print(f"   ❌ Errore: {str(e)}")
        return f"❌ Errore di connessione. Riprova tra poco."
