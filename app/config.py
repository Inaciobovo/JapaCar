import os
import secrets
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Comprimento minimo aceitavel para a chave de assinatura de sessao/CSRF. Com a
# SECRET_KEY conhecida, um atacante assina um cookie de sessao e entra no
# sistema sem senha, entao producao nao pode tolerar valor fraco ou previsivel.
SECRET_KEY_MINIMO = 32

# Valores de exemplo que ja-circulam no repositorio. Producao recusa qualquer
# um deles, mesmo que a variavel de ambiente esteja "preenchida".
SECRET_KEYS_CONHECIDAS = frozenset(
    {
        "troque-esta-chave-em-producao",
        "mude-esta-chave",
        "japacar-dev-secret-change-me",
    }
)


class ErroDeConfiguracao(RuntimeError):
    """Configuracao insegura impedindo o boot do app em producao."""


def _as_int(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def validar_config(config, ambiente):
    """Recusa o boot em producao quando a configuracao e insegura.

    Recebe o config ja montado pelo `create_app` (ou seja, depois das overrides
    de teste e da leitura do ambiente), e nao a classe — `from_object` do Flask
    nao instancia a config, entao validar dentro de `__init__` nunca rodaria.
    """
    if ambiente != "prod":
        return config

    chave = config.get("SECRET_KEY")
    if not chave:
        raise ErroDeConfiguracao(
            "SECRET_KEY nao definida. Gere uma com: "
            'python -c "import secrets; print(secrets.token_urlsafe(64))"'
        )
    if len(chave) < SECRET_KEY_MINIMO:
        raise ErroDeConfiguracao(
            f"SECRET_KEY muito curta ({len(chave)} caracteres; "
            f"minimo {SECRET_KEY_MINIMO})."
        )
    if chave in SECRET_KEYS_CONHECIDAS:
        raise ErroDeConfiguracao(
            "SECRET_KEY e um valor de exemplo conhecido. Gere uma chave "
            "unica para este ambiente."
        )
    if config.get("DEBUG"):
        raise ErroDeConfiguracao("DEBUG nao pode ser verdadeiro em producao.")
    if not config.get("SESSION_COOKIE_SECURE"):
        raise ErroDeConfiguracao(
            "SESSION_COOKIE_SECURE precisa ser True em producao."
        )
    if config.get("SEED_ON_STARTUP"):
        raise ErroDeConfiguracao(
            "SEED_ON_STARTUP nao pode ser verdadeiro em producao: ele cria "
            "admin/admin123. Crie o primeiro usuario com `flask usuario-criar`."
        )
    if not config.get("TRUSTED_HOSTS"):
        raise ErroDeConfiguracao(
            "TRUSTED_HOSTS/APP_DOMAIN nao definido em producao. Sem uma lista "
            "de hosts confiaveis, o Flask aceita qualquer Host header, o que "
            "permite envenenar links e cache. Defina APP_DOMAIN no .env."
        )
    return config


class Config:
    # Nenhuma chave de exemplo fica escrita no código. Sem SECRET_KEY no
    # ambiente, geramos uma aleatória por processo: em dev o preço é perder a
    # sessão a cada reinício, e a alternativa seria um segredo adivinhável
    # guardado no repositório. Em produção a ausência aborta o boot
    # (ver validar_config).
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_urlsafe(64)

    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    UPLOAD_DIR = os.environ.get("UPLOAD_DIR", str(BASE_DIR / "uploads"))

    # --- Upload de fotos -------------------------------------------------
    UPLOAD_MAX_FILE_SIZE = 10 * 1024 * 1024
    # Allowlist estrita. Fica de proposito sem .html, .svg e .js: servidos na
    # origem do sistema, eles executam script e viram XSS armazenado. O limite
    # acima de 5 tambem e aplicado no servidor, nao so no JavaScript.
    UPLOAD_EXTENSOES_PERMITIDAS = frozenset({".jpg", ".jpeg", ".png", ".webp", ".gif"})
    UPLOAD_MAX_FILES = 5

    # --- Sessao ---------------------------------------------------------
    # Secure + HttpOnly + SameSite=Lax sao o piso de seguranca do cookie de
    # sessao: nao trafega em HTTP puro, nao e legivel por JavaScript e nao
    # acompanha POST de origem cruzada.
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_NAME = "japacar_session"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_REFRESH_EACH_REQUEST = True

    # --- Limitacao de requisicoes ---------------------------------------
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URI = "memory://"
    # Teto geral por IP, bem acima do uso real de uma oficina (uma tela faz
    # poucos pedidos), mas abaixo do que um script de varredura consegue.
    RATELIMIT_DEFAULT = "600 per hour"
    # 5 tentativas por conta a cada 10 minutos. A chave combina IP e login
    # (ver app/limits.py), entao atacar um usuario inexistente nao trava o
    # admin — e um atacante nao faz password spray em 200 contas no mesmo IP.
    RATELIMIT_LOGIN = "5 per 10 minutes"
    RATELIMIT_LOGIN_MESSAGE = (
        "Muitas tentativas de login. Aguarde 10 minutos e tente novamente."
    )

    # --- Cabecalhos de seguranca ----------------------------------------
    # O Bootstrap e os icones sao servidos da propria origem (app/static), entao
    # a CSP nao precisa liberar nenhum CDN externo. Cada origem extra aqui e uma
    # superficie a mais para injecao de script.
    CSP = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "font-src 'self' data:; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'none'; "
        "object-src 'none'"
    )
    HSTS_MAX_AGE = 31536000

    # --- Host header confiavel ------------------------------------------
    # Sem esta lista o Flask aceita qualquer Host, o que permite envenenar
    # url_for em e-mails/redirecionamentos e cache. Em producao e alimentada
    # pelo `APP_DOMAIN` (ex.: japacar.duckdns.org); vazia em dev desativa a
    # checagem para nao atrapalhar localhost.
    #
    # `localhost`/`127.0.0.1` entram apenas quando ha um dominio configurado:
    # sao os hosts usados pelos healthchecks internos (curl local) e o app nao
    # publica porta, entao so o Caddy (na rede interna) os alcanca. Sem isso o
    # healthcheck do container tomaria 400 e o servico apareceria como unhealthy.
    _hosts_dominio = [
        host.strip()
        for host in (
            os.environ.get("TRUSTED_HOSTS")
            or os.environ.get("APP_DOMAIN")
            or ""
        ).split(",")
        if host.strip()
    ]
    TRUSTED_HOSTS = (
        _hosts_dominio + ["localhost", "127.0.0.1"] if _hosts_dominio else []
    )

    TZ = "America/Sao_Paulo"

    # Criar admin/admin123 no boot e o caminho mais curto para uma invasao.
    # Desligado por padrao; producao cria o primeiro usuario por comando.
    SEED_ON_STARTUP = os.environ.get("SEED_ON_STARTUP", "0") == "1"


class DevConfig(Config):
    DEBUG = True
    # Servir o dev por http:// sem Secure evita o "nao loga" classico quando
    # se roda o app local sem HTTPS.
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'japacar.db'}"
    )


class ProdConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:////app/data/japacar.db"
    )


CONFIG = {"dev": DevConfig, "prod": ProdConfig}
