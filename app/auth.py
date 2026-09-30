import bcrypt
from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import login_user, logout_user

from app.extensions import db, login_manager
from app.limits import chave_login, limiter
from app.models import Usuario

bp = Blueprint("auth", __name__)


def _limite_login():
    return current_app.config["RATELIMIT_LOGIN"]


def _mensagem_limite():
    return current_app.config["RATELIMIT_LOGIN_MESSAGE"]


def _excedeu(_limite_atingido=None):
    """429 vira a tela de login com o aviso, em vez de uma pagina crua do Werkzeug.

    O Flask-Limiter passa o `RateLimitItem` que estourou; o argumento existe
    para satisfazer essa assinatura e fica sem uso de propósito.
    """
    return redirect(url_for("auth.login", excedeu="true"))


def _eh_falha_de_login(resposta):
    """Conta a tentativa no limite só quando o login foi recusado.

    Sem isso, um operador que entra corretamente cinco vezes seguidas ficaria
    bloqueado — o limite existe para travar tentativa de adivinhação, não para
    limitar o uso legítimo.
    """
    if resposta.status_code == 429:
        return False
    destino = resposta.headers.get("Location", "")
    return "error=true" in destino


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(Usuario, int(user_id))
    except (TypeError, ValueError):
        return None


def verificar_senha(senha_bruta, hash_armazenado):
    if not hash_armazenado:
        return False
    try:
        return bcrypt.checkpw(
            senha_bruta.encode("utf-8"), hash_armazenado.encode("utf-8")
        )
    except (ValueError, AttributeError, TypeError):
        return False


@bp.get("/login")
def login():
    return render_template(
        "login.html",
        error=request.args.get("error") or None,
        logout=request.args.get("logout") or None,
        excedeu=request.args.get("excedeu") or None,
        mensagem_excedeu=_mensagem_limite(),
    )


@bp.post("/login")
@limiter.limit(
    _limite_login,
    key_func=chave_login,
    on_breach=_excedeu,
    # So a tentativa recusada conta: um login legitimo nao deve gastar cota.
    # A tentativa que disparou o limite tambem nao e contada, senao o usuario
    # ficaria preso por mais um ciclo de 10 minutos a cada recusa.
    deduct_when=_eh_falha_de_login,
)
def login_post():
    """Autentica o operador.

    A resposta e identica para "usuário inexistente" e "senha errada", e o
    tempo de resposta nao depende de o login existir: a consulta ao banco roda
    sempre e a comparacao de senha so ocorre quando ha hash. Isso evita
    enumeracao de contas por mensagem ou por tempo de resposta.

    O limite de tentativas vive no decorator acima, chaveado por IP + login.
    """
    username = (request.form.get("username") or "").strip()[:255]
    password = request.form.get("password") or ""

    usuario = db.session.execute(
        db.select(Usuario).where(Usuario.login == username)
    ).scalar_one_or_none()

    if usuario is not None and usuario.ativo and verificar_senha(password, usuario.senha):
        # Descarta qualquer estado da sessao anonima antes de autenticar
        # (anti session-fixing: um cookie plantado nao sobrevive ao login).
        session.clear()
        login_user(usuario, remember=False, fresh=True)
        return redirect(url_for("dashboard.dashboard"))

    return redirect(url_for("auth.login", error="true"))


@bp.post("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("auth.login", logout="true"))


def init_auth(app):
    app.register_blueprint(bp)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
