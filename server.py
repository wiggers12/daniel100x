from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import json
import os

# ===============================
# CONFIGURAÇÕES WHATSAPP
# ===============================
token = "EAALl2GJDMpMBPZBu8NmFIjWvqIDKJh4B1QlNsmG7n557ffCdCnNeXZBg1bR2bGFWo1CNZCXL5jiYXpfPZCZC8ZBGMbWUXw7vx4HykAPZBJ4bWczUa8ZClwKrPbCZBXgkW9DMemDkIqqCVO7BFNkoxZBjQu7nLQIkCUmu17J9zG8ZA5fgRX5RaK4ORLEdcYOo7vuRH1DZCwZDZD"
phone_id = "848088375057819"

# ===============================
# FLASK APP
# ===============================
app = Flask(__name__)
CORS(app)

# ===============================
# FIREBASE
# ===============================
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route("/")
def home():
    return "🔥 Servidor WhatsApp 7XX está rodando no Render!"

# ======================================================
# 1) ENDPOINT PARA BOAS-VINDAS AUTOMÁTICAS
# ======================================================
@app.route("/boasvindas", methods=["POST"])
def boasvindas():
    try:
        dados = request.get_json()
        nome = dados.get("nome")
        numero = dados.get("numero")

        print(f"📨 ENVIANDO TEMPLATE DE BOAS-VINDAS → {numero}")

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

        return jsonify({"status": "ok", "resposta": r.json()})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
# ======================================================
# 1.5) REENVIAR PARA QUEM AINDA NÃO RECEBEU
# ======================================================
@app.route("/reenviar_boasvindas", methods=["POST"])
def reenviar_boasvindas():
    try:
        usuarios = db.collection("usuarios").stream()
        enviados = []

        for u in usuarios:
            dados = u.to_dict()
            numero = dados.get("numero")
            nome = dados.get("nome")

            if dados.get("boas_vindas_enviada") == True:
                continue

            print(f"📨 Reenviando boas-vindas para {numero}")

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

            db.collection("usuarios").document(numero).update({
                "boas_vindas_enviada": True,
                "boas_vindas_data": firestore.SERVER_TIMESTAMP
            })

            enviados.append(numero)

        return jsonify({
            "status": "ok",
            "reenviados": enviados
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ======================================================
# 2) BROADCAST PARA TODOS USUÁRIOS
# ======================================================
@app.route("/enviar_massa", methods=["POST"])
def enviar_massa():
    try:
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
            "detalhes": enviados
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ======================================================
# 3) WEBHOOK OFICIAL DO WHATSAPP CLOUD
# ======================================================
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        token_enviado = request.args.get("hub.verify_token")
        desafio = request.args.get("hub.challenge")

        if token_enviado == "7xxsuperseguro":
            return desafio, 200
        return "Token inválido", 403

    elif request.method == "POST":
        data = request.json
        print("📥 WEBHOOK RECEBIDO:", data)
        return "EVENT_RECEIVED", 200


# ===============================
# EXECUTAR NO RENDER
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
