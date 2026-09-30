import os
from pathlib import Path

from flask import (
    Flask,
    current_app,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user
from flask_wtf.csrf import CSRFError
from werkzeug.middleware.proxy_fix import ProxyFix

from app.cli import register_cli
from app.config import CONFIG, ErroDeConfiguracao, validar_config
from app.context import inject_enums, inject_globals
from app.extensions import csrf, db, login_manager
from app.limits import init_limiter
from app.utils import format_brl, format_date, format_datetime

# Somente o que e realmente publico. `/uploads/` saiu daqui: as fotos de
# checklist mostram lataria e interiors de veiculos de clientes e ficavam
# acessiveis a qualquer visitante, sem sessao, pela mesma origem do sistema.
PUBLICOS = ("/login", "/css/", "/js/", "/img/", "/static/")


def create_app(config_name=None, **overrides):
    ambiente = config_name or os.environ.get("FLASK_ENV", "dev")
    _exigir_chave_de_ambiente(ambiente, overrides)
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(CONFIG.get(ambiente, CONFIG["dev"]))
    app.config.update(**overrides)
    # `validate_config` roda depois das overrides de proposito: e o config
    # efetivo que precisa ser seguro, nao a classe.
    validar_config(app.config, ambiente)
    app.url_map.strict_slashes = False

    if ambiente == "prod":
        # O Caddy encerra o TLS e fala com o Gunicorn em HTTP na rede interna.
        # Sem isto o Flask veria toda requisição como http:// e, entre outras
        # coisas, nunca enviaria o HSTS — o navegador aceitaria descer para HTTP
        # justamente quando o redirecionamento para https é o que protege.
        # Só um hop de proxy é confiável; a rede interna já é isolada.
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    csrf.init_app(app)
    init_limiter(app)

    _registrar_rotas(app)
    _registrar_estaticos(app)
    _registrar_filtros(app)
    _registrar_contexto(app)
    _registrar_seguranca(app)
    _registrar_erros(app)
    register_cli(app)

    with app.app_context():
        db.create_all()

        if app.config.get("SEED_ON_STARTUP", False):
            from app.cli import seed_users

            seed_users()

    return app


def _exigir_chave_de_ambiente(ambiente, overrides):
    """Produção só sobe com SECRET_KEY vinda de fora do código.

    A classe `Config` gera uma chave aleatória quando a variável não existe, e
    isso é o comportamento certo em dev. Se a mesma chave aleatória fosse aceita
    em produção, o app subiria sem erro e *toda* sessão existente seria
    invalidada a cada restart — o operador perceive como "o sistema cai" e não
    como "faltou configuração". Melhor abortar com mensagem explícita.
    """
    if ambiente != "prod":
        return
    if overrides.get("SECRET_KEY") or os.environ.get("SECRET_KEY"):
        return
    raise ErroDeConfiguracao(
        "SECRET_KEY nao definida no ambiente. Gere uma com: "
        'python -c "import secrets; print(secrets.token_urlsafe(64))" '
        "e salve no .env antes de subir em producao."
    )


def _registrar_rotas(app):
    from app.auth import bp as auth_bp
    from app.routes import (
        atendimentos,
        checklists,
        clientes,
        dashboard,
        despesas,
        orcamentos,
        relatorios,
        veiculos,
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(clientes.bp)
    app.register_blueprint(veiculos.bp)
    app.register_blueprint(atendimentos.bp)
    app.register_blueprint(orcamentos.bp)
    app.register_blueprint(checklists.bp)
    app.register_blueprint(despesas.bp)
    app.register_blueprint(relatorios.bp)


def _registrar_estaticos(app):
    static_dir = Path(app.static_folder).resolve()

    @app.get("/css/<path:filename>")
    def css(filename):
        return send_from_directory(static_dir / "css", filename)

    @app.get("/js/<path:filename>")
    def js(filename):
        return send_from_directory(static_dir / "js", filename)

    @app.get("/img/<path:filename>")
    def img(filename):
        return send_from_directory(static_dir / "img", filename)

    upload_dir = Path(app.config["UPLOAD_DIR"]).resolve()

    @app.get("/uploads/<path:filename>")
    def uploads(filename):
        """Entrega a foto do checklist somente para quem esta autenticado.

        O `before_request` global ja exige sessao em /uploads (nao esta mais em
        PUBLICOS); aqui ficam as garantias de que o arquivo sai como anexo
        imutavel e nunca e interpretado como documento pela origem do sistema.
        """
        resposta = make_response(
            send_from_directory(upload_dir, filename, max_age=0)
        )
        resposta.headers["X-Content-Type-Options"] = "nosniff"
        resposta.headers["Content-Disposition"] = (
            f'attachment; filename="{Path(filename).name}"'
        )
        resposta.headers["Cache-Control"] = "private, no-store"
        return resposta


def _registrar_filtros(app):
    @app.template_filter("brl")
    def brl(valor):
        return format_brl(valor)

    @app.template_filter("dt")
    def dt(valor, pattern="%d/%m/%Y %H:%M"):
        return format_datetime(valor, pattern)

    @app.template_filter("d")
    def d(valor):
        return format_date(valor)

    @app.template_filter("descricao")
    def descricao(tupla, valor):
        for chave, texto in tupla:
            if chave == valor:
                return texto
        return valor


def _registrar_contexto(app):
    @app.context_processor
    def dados_globais():
        return inject_globals()

    @app.context_processor
    def enums():
        return inject_enums()


def _registrar_seguranca(app):
    @app.before_request
    def exigir_login():
        if request.method == "OPTIONS":
            return None
        if not current_user.is_authenticated:
            for prefixo in PUBLICOS:
                if request.path == "/login" or request.path.startswith(prefixo):
                    return None
            return redirect(url_for("auth.login"))
        return None

    @app.after_request
    def cabecalhos_de_seguranca(resposta):
        """Cabecalhos aplicados a toda resposta, autenticada ou nao.

        `frame-ancestors 'none'` + `X-Frame-Options: DENY` fecham clickjacking:
        sem isso, um site externo embute `/atendimentos/<id>/finalizar` num
        iframe e o operador clica achando que esta no sistema, autorizando um
        recebimento na tela de quem esta logado.
        """
        config = current_app.config
        resposta.headers.setdefault("X-Content-Type-Options", "nosniff")
        resposta.headers.setdefault("X-Frame-Options", "DENY")
        resposta.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        resposta.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        resposta.headers.setdefault("Content-Security-Policy", config["CSP"])
        if request.is_secure:
            resposta.headers.setdefault(
                "Strict-Transport-Security",
                f"max-age={config['HSTS_MAX_AGE']}; includeSubDomains",
            )
        return resposta


def _registrar_erros(app):
    @app.errorhandler(CSRFError)
    def csrf_error(e):
        # `render_template` precisa estar importado: sem ele o handler estourava
        # NameError e toda falha de CSRF voltava 500 em vez da pagina 400.
        return (
            render_template("erro_csrf.html", descricao=e.description),
            400,
        )

    @app.errorhandler(403)
    def acesso_negado(e):
        return render_template("erro_acesso.html", pageTitle="Acesso negado"), 403

    @app.errorhandler(404)
    def nao_encontrado(e):
        if current_user.is_authenticated:
            return render_template("erro_acesso.html", pageTitle="Página não encontrada"), 404
        return render_template("erro_csrf.html", descricao="Página não encontrada."), 404

    @app.errorhandler(413)
    def requisicao_grande(e):
        return (
            render_template(
                "erro_acesso.html",
                pageTitle="Envio grande demais",
                mensagem="O arquivo enviado excede o limite permitido.",
            ),
            413,
        )
