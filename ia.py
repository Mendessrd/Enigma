from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==============================
# GERAR ENIGMA
# ==============================
def gerar_enigma(dificuldade="fácil"):
    prompt = f"""
    Crie um enigma {dificuldade}.
    Responda no formato:

    ENIGMA: ...
    RESPOSTA: ...
    DICA: ...
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    texto = response.choices[0].message.content

    enigma = texto.split("ENIGMA:")[1].split("RESPOSTA:")[0].strip()
    resposta = texto.split("RESPOSTA:")[1].split("DICA:")[0].strip()
    dica = texto.split("DICA:")[1].strip()

    return enigma, resposta, dica


# ==============================
# VALIDAR RESPOSTA
# ==============================
def validar_resposta(resposta_usuario, resposta_correta):
    prompt = f"""
    Resposta correta: {resposta_correta}
    Resposta do usuário: {resposta_usuario}

    Elas são equivalentes? Responda apenas SIM ou NÃO.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return "SIM" in response.choices[0].message.content.upper()
