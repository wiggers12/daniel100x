from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import json

# ===============================
# CONFIGURAÇÕES WHATSAPP
# ===============================
token = "EAALl2GJDMpMBPZBu8NmFIjWvqIDKJh4B1QlNsmG7n557ffCdCnNeXZBg1bR2bGFWo1CNZCXL5jiYXpfPZCZC8ZBGMbWUXw7vx4HykAPZBJ4bWczUa8ZClwKrPbCZBXgkW9DMemDkIqqCVO7BFNkoxZBjQu7nLQIkCUmu17J9zG8ZA5fgRX5RaK4ORLEdcYOo7vuRH1DZCwZDZD"
phone_id = "848088375057819"

# ===============================
# FIREBASE
# ===============================
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ===============================
# FLASK
# ===============================
app = Flask(__name__)

@app.route("/")
def home():
    return "🔥 Servidor WhatsApp 7XX rodando no Render!"

# ======================================================
# 1) ENDPOINT PARA BOAS-VINDAS AUTOMÁTICAS
# ======================================================
@app.route("/boasvindas", methods=["POST"])
def boasvindas():
    dados = request.get_json()
    nome = dados.get("nome")
    numero = dados.get("numero")

    print(f"📨 Enviando template de boas-vindas para: {numero} ({nome})")

    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "template",
        "template": {
            "name": "boas_vindas_7xx",
            "language": {"code": "pt_BR"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": nome}
                    ]
                }
            ]
        }
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    r = requests.post(url, json=payload, headers=headers)

    return jsonify({
        "status": "ok",
        "whatsapp": r.text
    })


# ======================================================
# 2) ENVIO EM MASSA PARA TODOS DO FIREBASE
# ======================================================
@app.route("/enviar_massa", methods=["POST"])
def enviar_massa():
    data = request.get_json()
    mensagem = data.get("mensagem")

    docs = db.collection("usuarios").stream()
    numeros = [doc.to_dict().get("numero") for doc in docs]

    enviados = []

    for numero in numeros:
        url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "text",
            "text": {"body": mensagem}
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        r = requests.post(url, json=payload, headers=headers)

        enviados.append({
            "numero": numero,
            "status": r.text
        })

    return jsonify({
        "status": "enviado",
        "total": len(enviados),
        "enviados": enviados
    })


# ===============================
# EXECUTAR NO RENDER
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
