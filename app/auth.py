import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def gerar_hash_senha(senha: str) -> str:
    salt = os.urandom(16)
    iteracoes = 100_000

    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt,
        iteracoes
    )

    salt_b64 = base64.b64encode(salt).decode("utf-8")
    hash_b64 = base64.b64encode(hash_bytes).decode("utf-8")

    return f"pbkdf2_sha256${iteracoes}${salt_b64}${hash_b64}"


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        algoritmo, iteracoes, salt_b64, hash_b64 = senha_hash.split("$")

        if algoritmo != "pbkdf2_sha256":
            return False

        salt = base64.b64decode(salt_b64)
        hash_original = base64.b64decode(hash_b64)

        novo_hash = hashlib.pbkdf2_hmac(
            "sha256",
            senha.encode("utf-8"),
            salt,
            int(iteracoes)
        )

        return hmac.compare_digest(novo_hash, hash_original)
    except Exception:
        return False


def criar_token_acesso(dados: dict) -> str:
    dados_token = dados.copy()

    expira_em = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    dados_token.update({
        "exp": expira_em
    })

    token = jwt.encode(
        dados_token,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def decodificar_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None