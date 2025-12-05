"""
Integrazione con Perplexity API
"""

import requests
from config import Config

def chiama_perplexity(messaggio_cliente, contesto_cliente=""):
    """
    Chiama Perplexity API per una risposta intelligente.
    Usato quando nessuna FAQ trova match.
    """
    
    # Se non hai key API configurata, torna risposta placeholder
    if not Config.PERPLEXITY_API_KEY or Config.PERPLEXITY_API_KEY.startswith("pplx-sk-"):
        return "🤖 Grazie per la domanda! Adesso rispondo in modo intelligente. (Configura PERPLEXITY_API_KEY per attivarmi)"
    
    prompt_system = f"""Sei un assistente di supporto clienti per una facility sportiva a Trieste.
Rispondi SEMPRE in italiano.
Risposte brevi (max 100 parole), professionali e amichevoli.
Contesto cliente: {contesto_cliente}
Usa emoji quando appropriate."""
    
    try:
        print(f"🤖 Chiamo Perplexity API...")
        
        response = requests.post(
            Config.PERPLEXITY_API_URL,
            headers={
                "Authorization": f"Bearer {Config.PERPLEXITY_API_KEY}",
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
        
        if response.status_code == 200:
            risposta = response.json()["choices"][0]["message"]["content"]
            print(f"✅ Risposta Perplexity ricevuta")
            return risposta
        else:
            print(f"❌ Errore Perplexity: {response.status_code}")
            return f"⚠️ Errore temporaneo. Riprovare tra poco."
    
    except requests.exceptions.Timeout:
        return "⏱️ Timeout - Il server è lento. Riprova tra poco."
    except Exception as e:
        print(f"❌ Errore Perplexity: {str(e)}")
        return f"❌ Errore di connessione. Dettagli: {str(e)}"
