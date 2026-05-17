import requests

from app.config import (
    WHATSAPP_TOKEN,
    WHATSAPP_PHONE_NUMBER_ID,
    WHATSAPP_API_VERSION
)


def extrair_mensagem_whatsapp(payload: dict):
    """
    Extrai dados principais de uma mensagem recebida pelo WhatsApp.

    Retorna:
    {
        "telefone": "...",
        "mensagem": "...",
        "tipo": "text|image|audio|video|document|sticker|unknown"
    }

    Se não encontrar mensagem válida, retorna None.
    """

    try:
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})

        messages = value.get("messages", [])

        if not messages:
            return None

        message = messages[0]

        telefone = message.get("from")
        tipo = message.get("type", "unknown")

        if tipo == "text":
            texto = message.get("text", {}).get("body", "")

            return {
                "telefone": telefone,
                "mensagem": texto,
                "tipo": tipo
            }

        mensagens_por_tipo = {
            "image": "O cliente enviou uma imagem.",
            "audio": "O cliente enviou um áudio.",
            "video": "O cliente enviou um vídeo.",
            "document": "O cliente enviou um documento.",
            "sticker": "O cliente enviou um sticker.",
            "location": "O cliente enviou uma localização.",
            "contacts": "O cliente enviou um contato.",
            "interactive": "O cliente enviou uma resposta interativa."
        }

        mensagem_formatada = mensagens_por_tipo.get(
            tipo,
            f"O cliente enviou uma mensagem do tipo: {tipo}."
        )

        return {
            "telefone": telefone,
            "mensagem": mensagem_formatada,
            "tipo": tipo
        }

    except Exception:
        return None


def enviar_mensagem_whatsapp(telefone: str, mensagem: str):
    """
    Envia uma mensagem de texto pelo WhatsApp Cloud API.

    Por enquanto, essa função já fica pronta, mas só funcionará quando
    WHATSAPP_TOKEN e WHATSAPP_PHONE_NUMBER_ID estiverem configurados.
    """

    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        return {
            "enviado": False,
            "motivo": "Token ou Phone Number ID não configurado."
        }

    url = (
        f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/"
        f"{WHATSAPP_PHONE_NUMBER_ID}/messages"
    )

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    body = {
        "messaging_product": "whatsapp",
        "to": telefone,
        "type": "text",
        "text": {
            "body": mensagem
        }
    }

    try:
        resposta = requests.post(url, headers=headers, json=body, timeout=15)

        return {
            "enviado": resposta.status_code in [200, 201],
            "status_code": resposta.status_code,
            "resposta": resposta.json()
        }

    except Exception as erro:
        return {
            "enviado": False,
            "motivo": str(erro)
        }


def extrair_status_whatsapp(payload: dict):
    """
    Extrai eventos de status enviados pela Meta, como:
    sent, delivered, read ou failed.

    Retorna None se o payload não for de status.
    """

    try:
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})

        statuses = value.get("statuses", [])

        if not statuses:
            return None

        status_info = statuses[0]

        return {
            "id_mensagem": status_info.get("id"),
            "status": status_info.get("status"),
            "telefone": status_info.get("recipient_id"),
            "timestamp": status_info.get("timestamp"),
            "errors": status_info.get("errors", [])
        }

    except Exception:
        return None
