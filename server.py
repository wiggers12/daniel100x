from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import json
import os
from datetime import datetime

# ============================================================
# CONFIGURAÇÕES WHATSAPP
# ============================================================
token = "EAALl2GJDMpMBPZBu8NmFIjWvqIDKJh4B1QlNsmG7n557ffCdCnNeXZBg1bR2bGFWo1CNZCXL5jiYXpfPZCZC8ZBGMbWUXw7vx4HykAPZBJ4bWczUa8ZClwKrPbCZBXgkW9DMemDkIqqCVO7BFNkoxZBjQu7nLQIkCUmu17J9zG8ZA5fgRX5RaK4ORLEdcYOo7vuRH1DZCwZDZD"
phone_id = "848088375057819"

# ============================================================
# FLASK APP
# ============================================================
app = Flask(__name__)
CORS(app)

# ============================================================
# FIREBASE
# ============================================================
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route("/")
def home():
    return "🔥 Servidor WhatsApp 7XX + Firestore Conversas ATIVO!"

# ============================================================
# 1) ENVIO DE BOAS-VINDAS
# ============================================================
@app.route("/boasvindas", methods=["POST"])
def boasvindas():
    try:
        dados = request.get_json()
        nome = dados.get("nome")
        numero = dados.get("numero")

        print(f"📨 ENVIANDO TEMPLATE DE BOAS-VINDAS para {numero}")

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

        # grava NO HISTÓRICO (tipo enviada)
        db.collection("conversas").add({
            "numero": numero,
            "nome": nome,
            "texto": f"(TEMPLATE) Boas-vindas enviada",
            "tipo": "enviada",
            "horario": firestore.SERVER_TIMESTAMP
        })

        return jsonify({"status": "ok", "resposta": r.json()})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ============================================================
# REENVIAR BOAS-VINDAS PARA QUEM NÃO RECEBEU
# ============================================================
@app.route("/reenviar_boasvindas", methods=["POST"])
def reenviar_boasvindas():
    try:
        usuarios = db.collection("usuarios").stream()
        reenviados = []

        for u in usuarios:
            dados = u.to_dict()
            numero = dados.get("numero")
            nome = dados.get("nome")

            # Pular se já enviou
            if dados.get("boas_vindas_enviada") == True:
                continue

            print(f"🔁 Reenviando para {numero}")

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

            url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
            r = requests.post(url, json=payload, headers=headers)

            db.collection("usuarios").document(numero).update({
                "boas_vindas_enviada": True,
                "boas_vindas_data": firestore.SERVER_TIMESTAMP
            })

            reenviados.append(numero)

        return jsonify({"status": "ok", "reenviados": reenviados})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ============================================================
# 2) ENVIAR MENSAGEM NORMAL (PAINEL → WHATSAPP)
# ============================================================
@app.route("/enviar", methods=["POST"])
def enviar():
    try:
        data = request.json
        numero = data.get("numero")
        texto = data.get("texto")

        url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "text",
            "text": {"body": texto}
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        r = requests.post(url, json=payload, headers=headers)

        # salvar no Firestore
        db.collection("conversas").add({
            "numero": numero,
            "nome": "",
            "texto": texto,
            "tipo": "enviada",
            "horario": firestore.SERVER_TIMESTAMP
        })

        return jsonify({"ok": True})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500



# ============================================================
# 3) WEBHOOK → RECEBE MENSAGENS DO WHATSAPP
# ============================================================
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
        print("📥 WEBHOOK RECEBIDO:", json.dumps(data, indent=2))

        try:
            entry = data["entry"][0]
            change = entry["changes"][0]["value"]
            messages = change.get("messages")

            if messages:
                m = messages[0]
                numero = m["from"]
                texto = m["text"]["body"]
                nome = change["contacts"][0]["profile"]["name"]

                print(f"💬 Msg recebida de {nome}: {texto}")

                # salva no Firestore
                db.collection("conversas").add({
                    "numero": numero,
                    "nome": nome,
                    "texto": texto,
                    "tipo": "recebida",
                    "horario": firestore.SERVER_TIMESTAMP
                })

        except Exception as e:
            print("❌ Erro ao tratar mensagem:", e)

        return "EVENT_RECEIVED", 200


# ===============================================================
# RODAR NO RENDER
# ===============================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
