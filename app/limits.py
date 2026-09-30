"""Limitacao de requisicoes (Flask-Limiter).

O login nao tinha nenhuma protecao contra forca bruta: um POST por tentativa,
sem bloqueio de conta, sem contador e sem registro. Com a senha padrao
`admin123` publicada no README, isso e um login valido.

O limite do login e chaveado por IP **e** login, e nao so por IP, por dois
motivos: atacar um usuario inexistente nao pode trancar o acesso do admin, e
um atacante nao consegue fazer password spray em centenas de contas a partir
do mesmo IP. As duas metades sao necessarias.
"""

from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def chave_login():
    """Chave de rate limit do login: IP + conta tentada."""
    login = (request.form.get("username") or "").strip().lower()[:64]
    return f"login:{get_remote_address()}:{login}"


# Instancia unica do processo, inicializada por `init_limiter` no app factory.
# O storage e criado em `init_app`, entao cada `create_app` (e portanto cada
# teste) comeca com um contador limpo.
limiter = Limiter(key_func=get_remote_address)


def init_limiter(app):
    limiter.init_app(app)
    return limiter
