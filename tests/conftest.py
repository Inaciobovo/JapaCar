import re
import shutil
from pathlib import Path

import pytest
from flask.testing import FlaskClient

from app import create_app

from tests.seed_base import seed_dados_base

BASE_DIR = Path(__file__).resolve().parent.parent

TOKEN_RE = re.compile(r'name="csrf_token"\s+value="([^"]+)"')


@pytest.fixture
def app(tmp_path):
    db_copy = tmp_path / "japacar.db"
    shutil.copyfile(BASE_DIR / "japacar.db", db_copy)
    uploads = tmp_path / "uploads"
    uploads.mkdir()

    application = create_app(
        "dev",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_copy}",
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SEED_ON_STARTUP=False,
        UPLOAD_DIR=str(uploads),
    )
    seed_dados_base(application)
    return application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def login(client):
    def _login(username="admin", password="admin123"):
        return client.post(
            "/login", data={"username": username, "password": password}
        )

    return _login


# ---------------------------------------------------------------------------
# Fixtures de segurança
#
# A suíte legada roda com WTF_CSRF_ENABLED=False (ver fixture `app` acima), o
# que significa que nenhum teste existente exercita a proteção CSRF. As
# fixtures abaixo sobem um app separado com CSRF LIGADO, de modo que a suíte
# de segurança valide o comportamento real de produção.
# ---------------------------------------------------------------------------


class ClienteHttps(FlaskClient):
    """Cliente de teste que fala como um navegador real.

    Duas correções sobre o cliente padrão:

    1. **HTTPS**: com ``SESSION_COOKIE_SECURE=True`` o jar de cookies do
       Werkzeug se recusa a devolver o cookie de sessão em ``http://``, e a
       suíte de autorização cairia num falso "não autenticado". Em produção o
       Caddy termina o TLS e entrega tudo por https.

    2. **Referer**: o Flask-WTF 1.3 rejeita POST sem token que não tragam o
       cabeçalho ``Referer``. Um navegador de verdade sempre envia em POST de
       formulário, então o cliente precisa fazer o mesmo — senão os testes medem
       um cenário que não existe em produção.
    """

    def open(self, *args, **kwargs):
        kwargs.setdefault("base_url", "https://localhost")
        cabecalhos = dict(kwargs.pop("headers", None) or {})
        cabecalhos.setdefault("Referer", "https://localhost/")
        kwargs["headers"] = cabecalhos
        return super().open(*args, **kwargs)


@pytest.fixture
def app_seg(tmp_path):
    db_copy = tmp_path / "seg.db"
    shutil.copyfile(BASE_DIR / "japacar.db", db_copy)
    uploads = tmp_path / "uploads"
    uploads.mkdir()

    # Configuração `prod` de propósito: a suíte de segurança precisa medir o
    # que roda em produção (cookie Secure, CSP, HSTS, sem seed de usuário).
    # A SECRET_KEY é passada por override para satisfazer a validação de boot.
    application = create_app(
        "prod",
        SECRET_KEY="chave-de-teste-com-tamanho-suficiente-para-producao-1234",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_copy}",
        TESTING=True,
        WTF_CSRF_ENABLED=True,
        SEED_ON_STARTUP=False,
        UPLOAD_DIR=str(uploads),
        RATELIMIT_ENABLED=True,
    )
    application.test_client_class = ClienteHttps
    seed_dados_base(application)
    return application


@pytest.fixture
def client_seg(app_seg):
    return app_seg.test_client()


def extrair_csrf(html: str) -> str | None:
    """Pega o token CSRF do formulário de login, ou None se a página não tiver."""
    match = TOKEN_RE.search(html)
    return match.group(1) if match else None


def token_csrf(client) -> str:
    """Token CSRF válido da sessão corrente.

    Vale para qualquer formulário: o Flask-WTF assina todos os formulários da
    sessão com a mesma semente. Varre algumas páginas porque a resposta muda com
    o perfil — `/` é 403 para o mecânico e redireciona para o login quando não
    há sessão, mas toda página operacional inclui o formulário de logout no menu.
    """
    for caminho in ("/", "/atendimentos", "/clientes", "/login"):
        html = client.get(caminho, follow_redirects=True).get_data(as_text=True)
        token = extrair_csrf(html)
        if token:
            return token
    raise AssertionError("nenhuma página devolveu um token csrf_token")


@pytest.fixture
def csrf(client_seg):
    """Lê um token CSRF válido da página de login."""

    def _csrf():
        return extrair_csrf(client_seg.get("/login").get_data(as_text=True))

    return _csrf


@pytest.fixture
def login_csrf(client_seg):
    """Login que respeita o CSRF (extrai o token antes de enviar)."""

    def _login(username="admin", password="admin123"):
        token = extrair_csrf(client_seg.get("/login").get_data(as_text=True))
        return client_seg.post(
            "/login",
            data={"username": username, "password": password, "csrf_token": token},
        )

    return _login


@pytest.fixture
def como_admin(client_seg, login_csrf):
    login_csrf("admin", "admin123")
    return client_seg


@pytest.fixture
def como_mecanico(client_seg, login_csrf):
    login_csrf("mecanico", "mecanico123")
    return client_seg
