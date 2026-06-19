import jwt
import time
import os

SECRET = os.getenv("JWT_SECRET")

if not SECRET:
    raise ValueError(
        "JWT_SECRET não configurado"
    )


def gerar_token():

    payload = {
        "service": "processador",
        "exp": int(time.time()) + 3600
    }

    return jwt.encode(
        payload,
        SECRET,
        algorithm="HS256"
    )


def validar_token(token):

    try:

        return jwt.decode(
            token,
            SECRET,
            algorithms=["HS256"]
        )

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None