from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import json
import os
from datetime import datetime
import threading
import time

# ============================================================
# CONFIGURAÇÕES WHATSAPP
# ============================================================
token = "EAALl2GJDMpMBPZBu8NmFIjWvqIDKJh4B1QlNsmG7n557ffCdCnNeXZBg1bR2bGFWo1CNZCXL5jiYXpfPZCZC8ZBGMbWUXw7vx4HykAPZBJ4bWczUa8ZClwKrPbCZBXgkW9DMemDkIqqCVO7BFNkoxZBjQu7nLQIkCUmu17J9zG8ZA5fgRX5RaK4ORLEdcYOo7vuRH1DZCwZDZD"
phone_id = "848088375057819"

# ============================================================
# FLASK APP
# ============================================================
app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})


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
# 1) ENVIO DE BOAS-VINDAS (Mantido, mas o /enviar é a prioridade)
# ============================================================
@app.route("/boasvindas", methods=["POST"])
def boasvindas():
    if not db:
        return jsonify({"erro": "Firebase não inicializado."}), 500
        
    try:
        dados = request.get_json()
        nome = dados.get("nome")
        numero = dados.get("numero")

        print(f"📨 ENVIANDO TEMPLATE DE BOAS-VINDAS para {numero}")

        url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"

        # Payload para TEMPLATE: 'boas_vindas_7xx' com 1 variável
        payload = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "template",
            "template": {
                "name": "boas_vindas_7xx",
                "language": {"code": "pt_BR"},
                "components": [
                    {"type": "body", "parameters": [{"type": "text", "text": nome}]}
                ]
            }
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        r = requests.post(url, json=payload, headers=headers)
        
        if r.status_code != 200:
             print(f"ERRO API WHATSAPP em /boasvindas: {r.text}")
             return jsonify({"status": "error", "whatsapp_error": r.json()}), 500

        # Log no Firestore
        db.collection("conversas").add({
            "numero": numero,
            "nome": nome,
            "texto": "(TEMPLATE) Boas-vindas enviada",
            "tipo": "enviada",
            "horario": firestore.SERVER_TIMESTAMP
        })

        return jsonify({"status": "ok", "resposta": r.json()})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ============================================================
# REENVIAR BOAS-VINDAS
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
                        {"type": "body", "parameters": [{"type": "text", "text": nome}]}
                    ]
                }
            }

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
            requests.post(url, json=payload, headers=headers)

            db.collection("usuarios").document(numero).update({
                "boas_vindas_enviada": True,
                "boas_vindas_data": firestore.SERVER_TIMESTAMP
            })

            reenviados.append(numero)

        return jsonify({"status": "ok", "reenviados": reenviados})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ============================================================
# FUNÇÃO AUTOMÁTICA PARA ENVIAR TEXTO
# ============================================================
# Nota: Esta função só é usada DENTRO DO WEBHOOK (onde a janela de 24h está aberta)
def enviar_mensagem_whatsapp(numero, texto):
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texto}
    }

    r = requests.post(url, json=data, headers=headers)
    
    if r.status_code != 200:
        # Se houver falha na resposta automática, logue (mas não interrompa o webhook)
        print(f"AVISO: Falha na resposta automática no webhook. Status: {r.status_code}. Detalhes: {r.text}")


# ============================================================
# 2) ENVIAR MENSAGEM NORMAL (PAINEL)
# ============================================================
@app.route("/enviar", methods=["POST", "OPTIONS"])
def enviar():
    if request.method == "OPTIONS":
        # Esta parte é importante para o CORS do painel.
        response = jsonify({"allow": True})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response, 200

    if not db:
        return jsonify({"erro": "Firebase não inicializado."}), 500

    try:
        data = request.json
        numero = data.get("numero")
        texto = data.get("texto", "") # Conteúdo da mensagem simples
        
        # 🆕 NOVOS PARÂMETROS PARA SUPORTE A TEMPLATE:
        template_solicitado = data.get("template_name") 
        nome_usuario = data.get("nome_usuario", "")    # O valor para o {{1}}

        url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # --- Lógica Condicional: Template VS Texto Simples ---
        
        if template_solicitado == "boas_vindas_7xx":
            # Payload TEMPLATE: Usado para reengajamento (fora da janela de 24h)
            if not nome_usuario:
                 return jsonify({"status": "error", "message": "O campo 'nome_usuario' é obrigatório para o template 'boas_vindas_7xx'."}), 400

            payload = {
                "messaging_product": "whatsapp",
                "to": numero,
                "type": "template",
                "template": {
                    "name": "boas_vindas_7xx",
                    "language": {"code": "pt_BR"},
                    "components": [
                        {"type": "body", "parameters": [{"type": "text", "text": nome_usuario}]}
                    ]
                }
            }
            texto_para_db = f"[TEMPLATE: {template_solicitado}] Enviado para {nome_usuario}"
            
        else:
            # Payload TEXTO SIMPLES: Usado dentro da janela de 24h
            if not texto:
                return jsonify({"status": "error", "message": "O campo 'texto' é obrigatório para mensagens simples."}), 400
            
            payload = {
                "messaging_product": "whatsapp",
                "to": numero,
                "type": "text",
                "text": {"body": texto}
            }
            texto_para_db = texto
            nome_usuario = "" # Não logamos nome_usuario se for texto simples

        # --- ENVIO ---
        r = requests.post(url, json=payload, headers=headers)
        
        # Tratamento de erro da API do WhatsApp
        if r.status_code != 200:
             # O erro 131047 virá aqui se você tentar enviar 'texto' fora da janela
             print(f"ERRO FATAL API WHATSAPP (Rota /enviar): Status {r.status_code}. Detalhes: {r.text}")
             return jsonify({"status": "error", "whatsapp_error": r.json()}), 500

        # Log no Firestore
        db.collection("conversas").add({
            "numero": numero,
            "nome": nome_usuario,
            "texto": texto_para_db,
            "tipo": "enviada",
            "horario": firestore.SERVER_TIMESTAMP
        })

        return jsonify({"ok": True}), 200

    except Exception as e:
        print(f"Erro interno na rota /enviar: {e}")
        return jsonify({"erro": str(e)}), 500


# ============================================================
# FUNÇÃO PARA PROCESSAR TUDO EM BACKGROUND
# (Precisa ser definida fora da rota /webhook)
# ============================================================
def processar_mensagem_recebida(numero, nome, tipo_mensagem, texto, data_completa_webhook):
    # ⚠️ Esta função é executada por um thread.
    try:
        if not db:
            print("❌ Firebase não inicializado no thread de processamento.")
            return

        # 1. Criar/Atualizar Usuário e Última Interação
        userRef = db.collection("usuarios").document(numero)
        if not userRef.get().exists:
            userRef.set({
                "nome": nome,
                "numero": numero,
                "criado": firestore.SERVER_TIMESTAMP,
                "boas_vindas_enviada": False,
                "ultima_interacao": firestore.SERVER_TIMESTAMP
            })
        else:
            userRef.update({"ultima_interacao": firestore.SERVER_TIMESTAMP})

        # 2. Salvar mensagem recebida
        db.collection("conversas").add({
            "numero": numero,
            "nome": nome,
            "texto": texto,
            "tipo": "recebida",
            "horario": firestore.SERVER_TIMESTAMP
        })

        # 3. Enviar a Mensagem Automática de Confirmação (I/O)
        resposta = "Mensagem recebida! 👍\nSua dúvida será respondida em breve."
        enviar_mensagem_whatsapp(numero, resposta)

        # 4. Salvar o log da mensagem enviada
        db.collection("conversas").add({
            "numero": numero,
            "nome": nome,
            "texto": resposta,
            "tipo": "enviada",
            "horario": firestore.SERVER_TIMESTAMP
        })
        
        print(f"✅ Processamento de {numero} concluído em background.")

    except Exception as e:
        print(f"❌ Erro CRÍTICO no thread de processamento: {e}")


# ============================================================
# 3) WEBHOOK – RECEBER MENSAGENS WHATSAPP - OTIMIZADO
# ============================================================
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == "7xxsuperseguro":
            return request.args.get("hub.challenge"), 200
        return "Token inválido", 403

    elif request.method == "POST":
        data = request.json
        print("📥 WEBHOOK RECEBIDO:", json.dumps(data, indent=2))
        
        if not db:
            print("❌ Firebase não inicializado no webhook. Retornando 200 OK.")
            # Sempre retorna 200 OK para o Meta para evitar desativação.
            return "EVENT_RECEIVED", 200

        try:
            entry = data["entry"][0]
            change = entry["changes"][0]["value"]
            messages = change.get("messages")

            if messages:
                m = messages[0]
                numero = m["from"]
                nome = change["contacts"][0]["profile"]["name"]
                tipo_mensagem = m.get("type")
                
                # --- LÓGICA DE EXTRAÇÃO DE TEXTO/LEGENDA ---
                if tipo_mensagem == "text":
                    texto = m["text"]["body"]
                elif tipo_mensagem in ["image", "video", "document", "audio"]:
                    media_data = m.get(tipo_mensagem, {})
                    texto = media_data.get("caption") or f"({tipo_mensagem.capitalize()} recebida sem legenda)"
                elif tipo_mensagem == "sticker":
                    texto = f"(Sticker recebido. ID: {m.get('sticker', {}).get('id', 'N/A')})"
                elif tipo_mensagem == "location":
                    texto = f"(Localização recebida. Nome: {m.get('location', {}).get('name', 'N/A')})"
                elif tipo_mensagem == "unsupported":
                    texto = "(Mensagem não suportada)"
                else:
                    texto = f'(Tipo de mensagem não processado: {tipo_mensagem})'

                print(f"💬 Recebida de {nome} ({tipo_mensagem}): {texto}")
                
                # ⭐️ Inicia o processamento pesado em um novo thread (assíncrono)
                # O thread faz o I/O demorado (Firebase e chamadas de API)
                threading.Thread(
                    target=processar_mensagem_recebida, 
                    args=(numero, nome, tipo_mensagem, texto, data)
                ).start()
                
        except Exception as e:
            # Captura erros de parsing ou estrutura do webhook
            print("❌ Erro de Parsing/Estrutura no webhook (antes do thread):", e)

        # ⭐️ Retorno rápido 200 OK. ISSO É A CHAVE para manter o webhook ativo.
        return "EVENT_RECEIVED", 200




# ============================================================
# EXECUTAR
# ============================================================
# Correção do Código Flask para usar a porta do ambiente
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000)) # Pega a variável de ambiente PORT
    app.run(host="0.0.0.0", port=port)
