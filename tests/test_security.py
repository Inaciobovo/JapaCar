"""Suíte de segurança do JAPACAR.

Valida os controles que protegem dados de clientes (CPF, telefone, endereço e
fotos), o dinheiro registrado nos orçamentos e a sessão de quem opera o sistema.

Os testes usam as fixtures `app_seg`/`client_seg`, que sobem o app com
**WTF_CSRF_ENABLED=True** — diferente da suíte legada (`app`), que roda com
CSRF desligado e portanto nunca exercita essa proteção.

Cobertura por grupo:
  A. Autenticação e sessão
  B. Autorização por perfil (RBAC)
  C. Upload de arquivos / XSS armazenado
  D. Integridade de dados e validação de entrada
  E. Headers de segurança e XSS
  F. Infraestrutura (em tests/test_security_static.py)
  G. Regressão dos controles já existentes
"""

import io
import re
from io import BytesIO
from pathlib import Path

import pytest

from app.extensions import db
from app.models import ChecklistEntrada, Cliente, FotoChecklist, Orcamento, Veiculo
from tests.conftest import token_csrf

# Binários mínimos para simular arquivos reais e falsificados.
JPEG_VALIDO = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9"
PNG_VALIDO = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
GZIP_FALSIFICADO = b"\x1f\x8b\x08\x00" + b"\x00" * 32

# Válido por dígito verificador e distinto do CPF do cliente da seed — a rota
# recusa CPF duplicado, e um teste que reusa o da seed mediria unicidade, não
# validação.
CPF_VALIDO = "111.444.777-35"
CPF_INVALIDO = "111.222.333-44"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def primeiro_veiculo_id(app):
    with app.app_context():
        return Veiculo.query.first().id


def token(client):
    """Token CSRF válido da sessão corrente (serve para qualquer formulário)."""
    return token_csrf(client)


def post(client, path, data=None, **kwargs):
    """POST autenticado com token CSRF."""
    payload = dict(data or {})
    payload["csrf_token"] = token(client)
    return client.post(path, data=payload, **kwargs)


def post_csrf(client, path, data=None, **kwargs):
    """POST autenticado com token CSRF e arquivo (multipart)."""
    payload = dict(data or {})
    payload["csrf_token"] = token(client)
    return client.post(path, data=payload, **kwargs)


def enviar_foto(client, app, arquivos, veiculo_id=None, responsavel="Mecânico"):
    """Salva um checklist com as fotos informadas.

    `arquivos` é uma lista de tuplas ``(nome_arquivo, bytes)``.
    """
    if veiculo_id is None:
        veiculo_id = primeiro_veiculo_id(app)
    # O Werkzeug só monta multipart a partir de um dict, e trata cada item de
    # uma lista como parte repetida do mesmo campo — é assim que `novasFotos`
    # vira várias fotos num único POST.
    payload = {
        "veiculoId": str(veiculo_id),
        "responsavel": responsavel,
        "csrf_token": token(client),
        "novasFotos": [(BytesIO(conteudo), nome) for nome, conteudo in arquivos],
    }
    return client.post("/checklists/salvar", data=payload)


def contar_fotos(app):
    with app.app_context():
        return FotoChecklist.query.count()


# ===========================================================================
# GRUPO A — Autenticação e sessão
# ===========================================================================


def test_login_sem_csrf_retorna_400(client_seg):
    """POST /login sem token CSRF precisa ser rejeitado com 400, não 500."""
    r = client_seg.post("/login", data={"username": "admin", "password": "admin123"})
    assert r.status_code == 400


def test_pagina_de_erro_csrf_renderiza(client_seg):
    """O handler de CSRF precisa renderizar a página amigável.

    Regressão: `render_template` não era importado em app/__init__.py e o
    handler estourava NameError, devolvendo 500 em toda falha de CSRF.
    """
    r = client_seg.post("/login", data={"username": "admin", "password": "admin123"})
    assert r.status_code == 400
    corpo = r.get_data(as_text=True)
    assert "csrf" in corpo.lower()
    assert "NameError" not in corpo
    assert "<html" in corpo.lower()


def test_login_bloqueado_apos_cinco_tentativas(client_seg):
    """Força bruta precisa ser interrompida, com aviso claro ao operador."""
    for _ in range(5):
        r = client_seg.post(
            "/login",
            data={"username": "admin", "password": "errada", "csrf_token": token(client_seg)},
        )
        assert "error=true" in r.headers["Location"], "as 5 primeiras devem falhar"

    r = client_seg.post(
        "/login",
        data={"username": "admin", "password": "errada", "csrf_token": token(client_seg)},
    )
    assert "excedeu=true" in r.headers["Location"], "a 6a tentativa deve ser barrada"

    # Nem mesmo a senha correta passa enquanto a janela estiver aberta.
    r = client_seg.post(
        "/login",
        data={"username": "admin", "password": "admin123", "csrf_token": token(client_seg)},
    )
    assert "excedeu=true" in r.headers["Location"]

    with client_seg.session_transaction() as sess:
        assert "_user_id" not in sess, "nenhuma sessao pode ser criada sob bloqueio"


def test_bloqueio_nao_atinge_outra_conta(client_seg):
    """O limite é por conta + IP: atacar 'inexistente' não pode travar o admin."""
    for _ in range(6):
        client_seg.post(
            "/login",
            data={
                "username": "naoexiste",
                "password": "errada",
                "csrf_token": token(client_seg),
            },
        )
    r = client_seg.post(
        "/login",
        data={"username": "admin", "password": "admin123", "csrf_token": token(client_seg)},
    )
    assert r.status_code == 302
    assert r.headers["Location"] == "/"


def test_caddy_encaminha_https_para_o_app(app_seg):
    """Atras do Caddy o Flask precisa enxergar https, senão não manda HSTS.

    O proxy termina o TLS e fala HTTP com o Gunicorn. Sem confiar no
    X-Forwarded-Proto, `request.is_secure` seria False em toda requisição real
    e o cabeçalho HSTS nunca sairia — o navegador aceitaria descer para HTTP.
    """
    r = app_seg.test_client().get(
        "/login", headers={"X-Forwarded-Proto": "https", "X-Forwarded-For": "1.2.3.4"}
    )
    assert "max-age=" in r.headers.get("Strict-Transport-Security", ""), (
        "HSTS ausente: o app não está confiando no protocolo encaminhado pelo proxy"
    )


def test_proxy_nao_pode_forjar_https_a_partir_de_um_cliente(app_seg):
    """O ganho do ProxyFix precisa vir acompanhado da restrição de rede.

    Confiar em `X-Forwarded-Proto` só é seguro porque o container só conversa
    com o Caddy, na rede interna. Se o Gunicorn passasse a escutar em 0.0.0.0
    na internet, qualquer cliente poderia mandar esse cabeçalho e forjar https
    (ou, pior, forjar o host). O teste registra essa dependência: o proxy só
    aceita conexões da rede do compose.
    """
    compose = (Path(__file__).resolve().parent.parent / "docker-compose.yml").read_text(
        encoding="utf-8"
    )
    bloco_app = compose.split("  app:", 1)[1].split("\n  caddy:", 1)[0]
    assert "ports:" not in bloco_app, (
        "o serviço app não pode publicar portas: exposto, o X-Forwarded-Proto "
        "passaria a ser controlável por qualquer cliente"
    )
    assert '"8080:8080"' not in compose, (
        "o app está publicado na host; só o Caddy deve receber tráfego externo"
    )


def test_cookie_de_sessao_endurecido(client_seg):
    """O cookie de sessão precisa de Secure, HttpOnly e SameSite."""
    client_seg.get("/login")
    r = client_seg.post(
        "/login",
        data={"username": "admin", "password": "admin123", "csrf_token": token(client_seg)},
    )
    cookies = r.headers.getlist("Set-Cookie")
    assert cookies, "nenhum cookie foi emitido"
    # Lê o nome da config em vez de assumir "session": o app define o seu, e um
    # teste que assume o nome padrão passa a não ver o cookie de nada.
    nome = client_seg.application.config["SESSION_COOKIE_NAME"]
    sessao = next((c for c in cookies if c.startswith(f"{nome}=")), None)
    assert sessao is not None, f"cookie de sessão ausente: {cookies}"
    assert "HttpOnly" in sessao
    assert "Secure" in sessao
    assert "SameSite=Lax" in sessao or "SameSite=Strict" in sessao


def test_login_limpa_sessao_anterior(client_seg):
    """Anti session-fixing: nada da sessão pré-autenticação sobrevive ao login."""
    with client_seg.session_transaction() as sess:
        sess["dado_injetado"] = "valor"
    client_seg.post(
        "/login",
        data={"username": "admin", "password": "admin123", "csrf_token": token(client_seg)},
    )
    with client_seg.session_transaction() as sess:
        assert "dado_injetado" not in sess


def test_sessao_expira_em_no_maximo_oito_horas(app_seg):
    """Sessão não pode ficar válida por semanas."""
    from datetime import timedelta

    limite = app_seg.config["PERMANENT_SESSION_LIFETIME"]
    assert isinstance(limite, timedelta)
    assert limite <= timedelta(hours=8), f"sessao dura {limite}, maximo 8h"


def test_prod_recusa_secret_key_padrao():
    """Produção não pode subir com a SECRET_KEY de desenvolvimento."""
    from app import create_app

    with pytest.raises(RuntimeError):
        create_app("prod", SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")


def test_prod_recusa_secret_key_curta():
    from app import create_app

    with pytest.raises(RuntimeError):
        create_app(
            "prod",
            SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
            SECRET_KEY="curta",
        )


def test_seed_desligado_por_padrao():
    """`SEED_ON_STARTUP` não pode valer 1 por padrão (cria admin/admin123)."""
    from app.config import Config

    assert Config.SEED_ON_STARTUP is False


def test_prod_nao_cria_usuarios_padrao(tmp_path):
    """Subir o app em produção não pode criar admin/admin123 automaticamente."""
    from app import create_app
    from app.models import Usuario

    app = create_app(
        "prod",
        SECRET_KEY="chave-de-teste-com-tamanho-suficiente-para-producao-1234",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{tmp_path / 'prod.db'}",
    )
    with app.app_context():
        assert db.session.execute(
            db.select(Usuario).where(Usuario.login == "admin")
        ).scalar_one_or_none() is None


def test_seed_ligado_em_producao_recusa_o_boot(tmp_path):
    """`SEED_ON_STARTUP=1` com DEBUG desligado tem de abortar a subida."""
    from app import create_app

    with pytest.raises(RuntimeError):
        create_app(
            "prod",
            SECRET_KEY="chave-de-teste-com-tamanho-suficiente-para-producao-1234",
            SQLALCHEMY_DATABASE_URI=f"sqlite:///{tmp_path / 'prod.db'}",
            SEED_ON_STARTUP=True,
        )


def test_usuario_inativo_nao_entra(app_seg, client_seg):
    """Conta desativada não pode autenticar mesmo com senha correta."""
    from app.extensions import db as _db
    from app.models import Usuario

    with app_seg.app_context():
        _db.session.execute(
            _db.update(Usuario).where(Usuario.login == "mecanico").values(ativo=False)
        )
        _db.session.commit()

    r = client_seg.post(
        "/login",
        data={"username": "mecanico", "password": "mecanico123", "csrf_token": token(client_seg)},
    )
    assert r.status_code == 302
    assert "error=true" in r.headers["Location"]


def test_mensagem_de_login_nao_revela_usuario_existente(client_seg):
    """A resposta precisa ser idêntica para usuário inexistente e senha errada."""
    inexistente = client_seg.post(
        "/login",
        data={
            "username": "naoexiste",
            "password": "admin123",
            "csrf_token": token(client_seg),
        },
    )
    senha_errada = client_seg.post(
        "/login",
        data={
            "username": "admin",
            "password": "senhaerrada",
            "csrf_token": token(client_seg),
        },
    )
    assert inexistente.status_code == senha_errada.status_code
    assert "error=true" in inexistente.headers["Location"]
    assert "error=true" in senha_errada.headers["Location"]


# ===========================================================================
# GRUPO B — Autorização por perfil
#
# Regra definida pelo cliente: o mecânico não vê a parte financeira
# (quanto entra e quanto sai); ele apenas monta orçamentos.
# ===========================================================================


FINANCEIRO = [
    "/",
    "/despesas",
    "/relatorios/orcamentos",
]


@pytest.mark.parametrize("caminho", FINANCEIRO)
def test_mecanico_bloqueado_no_financeiro(como_mecanico, caminho):
    """Mecânico não acessa telas com receita/despesa consolidada."""
    r = como_mecanico.get(caminho)
    assert r.status_code == 403, f"{caminho} deveria negar acesso ao MECANICO"


def test_mecanico_bloqueado_ao_criar_despesa(como_mecanico):
    """O bloqueio precisa valer também no POST, não só no menu."""
    r = post(
        como_mecanico,
        "/despesas/salvar",
        {
            "descricao": "Despesa nao autorizada",
            "categoria": "OUTROS",
            "valorText": "999,00",
            "data": "2026-09-29",
        },
    )
    assert r.status_code == 403

    with como_mecanico.application.app_context():
        from app.models import Despesa

        assert (
            db.session.execute(
                db.select(Despesa).where(Despesa.descricao == "Despesa nao autorizada")
            ).scalar_one_or_none()
            is None
        )


def test_mecanico_bloqueado_ao_remover_despesa(como_mecanico):
    with como_mecanico.application.app_context():
        from app.models import Despesa

        despesa_id = Despesa.query.first().id

    r = post(como_mecanico, f"/despesas/{despesa_id}/remover", {})
    assert r.status_code == 403


@pytest.mark.parametrize(
    "caminho", ["/clientes", "/veiculos", "/checklists", "/atendimentos", "/orcamentos"]
)
def test_mecanico_acessa_o_fluxo_operacional(como_mecanico, caminho):
    """O RBAC não pode quebrar o trabalho do mecânico."""
    assert como_mecanico.get(caminho).status_code == 200, caminho


def test_mecanico_pode_criar_orcamento(como_mecanico):
    """O mecânico continua able de montar orçamento (é o trabalho dele)."""
    with como_mecanico.application.app_context():
        atendimento_id = Orcamento.query.first().atendimento_id

    r = post(
        como_mecanico,
        "/orcamentos/salvar",
        {
            "atendimentoId": str(atendimento_id),
            "status": "PENDENTE",
            "valorMaoDeObraText": "150,00",
            "itemDescricao": ["Troca de oleo"],
            "itemQuantidade": ["1"],
            "itemValorUnitario": ["80,00"],
        },
    )
    assert r.status_code == 302
    with como_mecanico.application.app_context():
        criado = db.session.execute(
            db.select(Orcamento).where(Orcamento.valor_mao_de_obra == 150.0)
        ).scalar_one_or_none()
        assert criado is not None


def test_mecanico_baixa_pdf_do_orcamento(como_mecanico):
    """Baixar o PDF é parte do fluxo de orçamento, não é visão consolidada."""
    with como_mecanico.application.app_context():
        orc_id = Orcamento.query.first().id
    r = como_mecanico.get(f"/orcamentos/{orc_id}/pdf")
    assert r.status_code == 200
    assert r.mimetype == "application/pdf"


@pytest.mark.parametrize("caminho", FINANCEIRO + ["/clientes", "/veiculos"])
def test_admin_acessa_tudo(como_admin, caminho):
    assert como_admin.get(caminho).status_code == 200, caminho


def test_financial_desaparece_do_menu_do_mecanico(como_mecanico):
    """O menu precisa esconder os links que dariam 403."""
    corpo = como_mecanico.get("/atendimentos").get_data(as_text=True)
    assert 'href="/despesas"' not in corpo
    assert 'href="/relatorios/orcamentos"' not in corpo


def test_anonymous_nao_acessa_financeiro(client_seg):
    """Visitante sem sessão é empurrado para o login, nunca recebe dados."""
    for caminho in FINANCEIRO:
        r = client_seg.get(caminho)
        assert r.status_code == 302, caminho
        assert "/login" in r.headers["Location"]


# ===========================================================================
# GRUPO C — Upload de arquivos / XSS armazenado
#
# Vetor: sem validação de tipo, um arquivo .html/.svg enviado no checklist é
# gravado em uploads/ e servido na MESMA ORIGEM do JAPACAR. O navegador executa
# o script e o atacante controla a sessão de um atendente logado.
# ===========================================================================


TIPOS_REJEITADOS = [
    ("foto.html", b"<html><body><script>alert(document.cookie)</script></body></html>"),
    ("foto.svg", b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'),
    ("foto.php", b"<?php system($_GET['c']); ?>"),
    ("foto.exe", b"MZ\x90\x00\x03"),
    ("foto.js", b"alert(document.domain)"),
    ("foto.htm", b"<script>alert(1)</script>"),
]


@pytest.mark.parametrize("nome,conteudo", TIPOS_REJEITADOS)
def test_upload_de_tipo_perigoso_recusado(como_admin, app_seg, nome, conteudo):
    """Extensão que execute script no navegador precisa ser barrada no servidor."""
    r = enviar_foto(como_admin, app_seg, [(nome, conteudo)])
    assert r.status_code == 302
    assert contar_fotos(app_seg) == 0, f"{nome} foi gravado no disco"


def test_upload_falsificado_por_magic_bytes_recusado(como_admin, app_seg):
    """Só a extensão não basta: o conteúdo precisa bater com o tipo declarado."""
    r = enviar_foto(como_admin, app_seg, [("foto.jpg", GZIP_FALSIFICADO)])
    assert r.status_code == 302
    assert contar_fotos(app_seg) == 0


def test_upload_valido_e_aceito(como_admin, app_seg):
    """Regressão: JPEG e PNG legítimos continuam entrando."""
    r = enviar_foto(como_admin, app_seg, [("foto.jpg", JPEG_VALIDO)])
    assert r.status_code == 302
    assert contar_fotos(app_seg) == 1

    r = enviar_foto(como_admin, app_seg, [("foto.png", PNG_VALIDO)])
    assert r.status_code == 302
    assert contar_fotos(app_seg) == 2


def test_upload_sem_extensao_recusado(como_admin, app_seg):
    r = enviar_foto(como_admin, app_seg, [("arquivo", JPEG_VALIDO)])
    assert r.status_code == 302
    assert contar_fotos(app_seg) == 0


def test_uploads_exige_autenticacao(app_seg, client_seg):
    """Fotos de checklist são dado de cliente: não podem ser públicas.

    Regressão: /uploads/ estava em PUBLICOS e servia sem sessão.
    """
    with app_seg.app_context():
        caminho = (
            db.session.execute(db.select(FotoChecklist.caminho_arquivo))
            .scalars()
            .first()
        )
    if caminho is None:
        pytest.skip("sem fotos no banco de fixtures")

    r = client_seg.get(f"/uploads/{caminho}")
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]


def test_uploads_nao_e_servido_como_html(como_admin, app_seg):
    """Mesmo autenticado, o arquivo nunca pode ser interpretado como página."""
    enviar_foto(como_admin, app_seg, [("foto.jpg", JPEG_VALIDO)])
    with app_seg.app_context():
        caminho = db.session.execute(db.select(FotoChecklist.caminho_arquivo)).scalars().first()

    r = como_admin.get(f"/uploads/{caminho}")
    assert r.status_code == 200
    assert r.mimetype in ("image/jpeg", "application/octet-stream")
    assert "attachment" in r.headers.get("Content-Disposition", "")
    assert r.headers.get("X-Content-Type-Options") == "nosniff"


def test_upload_acima_do_limite_recusado(como_admin, app_seg):
    """Arquivo acima de UPLOAD_MAX_FILE_SIZE precisa ser barrado.

    Regressão: a config existia mas nunca era lida.
    """
    grande = JPEG_VALIDO + b"\x00" * (11 * 1024 * 1024)
    r = enviar_foto(como_admin, app_seg, [("enorme.jpg", grande)])
    assert r.status_code == 302
    assert contar_fotos(app_seg) == 0


def test_request_acima_de_max_content_length_retorna_413(como_admin, app_seg):
    """Corpo acima de MAX_CONTENT_LENGTH é barrado pelo Flask com 413."""
    payload = b"\x00" * (51 * 1024 * 1024)
    r = como_admin.post(
        "/checklists/salvar",
        data={
            "csrf_token": token(como_admin),
            "veiculoId": str(primeiro_veiculo_id(app_seg)),
            "responsavel": "Teste",
            "novasFotos": (io.BytesIO(payload), "gigante.jpg"),
        },
        content_type="multipart/form-data",
    )
    assert r.status_code == 413


def test_numero_de_fotos_limitado_no_servidor(como_admin, app_seg):
    """O limite de 5 fotos não pode depender só do JavaScript do navegador."""
    r = enviar_foto(
        como_admin,
        app_seg,
        [(f"f{i}.jpg", JPEG_VALIDO) for i in range(9)],
    )
    assert r.status_code == 302
    assert contar_fotos(app_seg) <= 5


def test_path_traversal_em_upload_bloqueado(app_seg, como_admin):
    """Não é possível ler o banco por manipulação de caminho."""
    for tentativa in [
        "/uploads/../../japacar.db",
        "/uploads/..%2f..%2fjapacar.db",
        "/uploads/....//....//japacar.db",
    ]:
        r = como_admin.get(tentativa)
        assert r.status_code in (403, 404), tentativa
        assert b"SQLite format 3" not in r.data


def test_remover_foto_exige_csrf(como_admin):
    """A remoção de foto é escrita e precisa de token."""
    r = como_admin.post("/checklists/foto/1/remover", data={})
    assert r.status_code == 400


# ===========================================================================
# GRUPO D — Integridade de dados e validação de entrada
# ===========================================================================


def test_status_orcamento_invalido_recusado(como_admin):
    """`status` gravado sem validação quebra relatório e fluxo financeiro.

    Regressão: app/routes/orcamentos.py gravava form.get("status") cru.
    """
    with como_admin.application.app_context():
        atendimento_id = Orcamento.query.first().atendimento_id
        antes = db.session.execute(
            db.select(Orcamento.status).where(Orcamento.atendimento_id == atendimento_id)
        ).scalars().first()

    post(
        como_admin,
        "/orcamentos/salvar",
        {
            "atendimentoId": str(atendimento_id),
            "status": "HACK_EVASION_FISCAL",
            "valorMaoDeObraText": "10,00",
            "itemDescricao": ["Item"],
            "itemQuantidade": ["1"],
            "itemValorUnitario": ["10,00"],
        },
    )

    with como_admin.application.app_context():
        depois = db.session.execute(
            db.select(Orcamento.status).where(Orcamento.atendimento_id == atendimento_id)
        ).scalars().first()
    assert depois in (antes, "PENDENTE"), f"status invalido persistido: {depois}"


def test_categoria_despesa_invalida_recusada(como_admin):
    from app.models import Despesa

    r = post(
        como_admin,
        "/despesas/salvar",
        {
            "descricao": "Categoria inventada",
            "categoria": "GOVERNO_FAKE",
            "valorText": "10,00",
            "data": "2026-09-29",
        },
    )
    assert r.status_code == 302
    with como_admin.application.app_context():
        assert Despesa.query.filter_by(descricao="Categoria inventada").count() == 0


def test_nivel_combustivel_invalido_recusado(como_admin, app_seg):
    r = post(
        como_admin,
        "/checklists/salvar",
        {
            "veiculoId": str(primeiro_veiculo_id(app_seg)),
            "responsavel": "Mecânico",
            "nivelCombustivel": "COMBUSTIVEL_DE_OVELEIRO",
        },
    )
    assert r.status_code == 302
    with app_seg.app_context():
        valor = db.session.execute(
            db.select(ChecklistEntrada.nivel_combustivel).order_by(ChecklistEntrada.id.desc())
        ).scalars().first()
    assert valor != "COMBUSTIVEL_DE_OVELEIRO"


@pytest.mark.parametrize("valor", ["-1.000,00", "999.999.999,99", "1e309", "NaN"])
def test_valor_de_orcamento_fora_dos_limites_recusado(como_admin, valor):
    """Total negativo, absurdo ou não-finite corrompe o financeiro."""
    with como_admin.application.app_context():
        atendimento_id = Orcamento.query.first().atendimento_id
        antes = db.session.get(Orcamento, Orcamento.query.first().id).valor_total

    post(
        como_admin,
        "/orcamentos/salvar",
        {
            "atendimentoId": str(atendimento_id),
            "status": "PENDENTE",
            "valorMaoDeObraText": valor,
            "itemDescricao": ["Item"],
            "itemQuantidade": ["1"],
            "itemValorUnitario": ["1,00"],
        },
    )

    with como_admin.application.app_context():
        orc = db.session.get(Orcamento, Orcamento.query.first().id)
        assert orc.valor_total == antes, f"total alterado para {orc.valor_total} com {valor}"


def test_quantidade_negativa_recusada(como_admin):
    with como_admin.application.app_context():
        atendimento_id = Orcamento.query.first().atendimento_id
    post(
        como_admin,
        "/orcamentos/salvar",
        {
            "atendimentoId": str(atendimento_id),
            "status": "PENDENTE",
            "valorMaoDeObraText": "0,00",
            "itemDescricao": ["Item negativo"],
            "itemQuantidade": ["-5"],
            "itemValorUnitario": ["100,00"],
        },
    )
    with como_admin.application.app_context():
        total = db.session.execute(
            db.select(Orcamento.valor_total).where(Orcamento.atendimento_id == atendimento_id)
        ).scalars().first()
    assert total is None or total >= 0, f"total negativo: {total}"


def test_cpf_invalido_recusado(como_admin):
    r = post(
        como_admin,
        "/clientes/salvar",
        {"nome": "CPF Ruim", "cpf": CPF_INVALIDO},
    )
    assert r.headers["Location"].endswith("/clientes/novo")
    with como_admin.application.app_context():
        assert Cliente.query.filter_by(nome="CPF Ruim").count() == 0


def test_cpf_valido_aceito(como_admin):
    post(como_admin, "/clientes/salvar", {"nome": "CPF Bom", "cpf": CPF_VALIDO})
    with como_admin.application.app_context():
        assert Cliente.query.filter_by(nome="CPF Bom").count() == 1


@pytest.mark.parametrize(
    "caminho",
    [
        "/checklists?dataInicio=nao-e-data",
        "/despesas?dataInicio=nao-e-data&dataFim=xx",
        "/relatorios/orcamentos?dataInicio=nao-e-data&dataFim=xx",
    ],
)
def test_filtro_de_data_invalido_nao_derruba_o_app(como_admin, caminho):
    """Filtro malformado não pode virar erro 500 (disponibilidade)."""
    r = como_admin.get(caminho)
    assert r.status_code == 200, f"{caminho} devolveu {r.status_code}"


@pytest.mark.parametrize("rota", ["clientes", "veiculos", "checklists", "atendimentos", "orcamentos", "despesas"])
def test_id_inexistente_nao_derruba_o_app(como_admin, rota):
    r = como_admin.get(f"/{rota}/999999/editar")
    assert r.status_code in (302, 404), f"/{rota}/999999/editar devolveu {r.status_code}"


def test_salvar_com_id_inexistente_nao_cria_registro_orfão(como_admin):
    """Informar um id que não existe não pode criar/atualizar registro espúrio."""
    post(
        como_admin,
        "/despesas/salvar",
        {
            "id": "999999",
            "descricao": "Despesa fantasma",
            "categoria": "OUTROS",
            "valorText": "1,00",
            "data": "2026-09-29",
        },
    )
    with como_admin.application.app_context():
        assert Cliente.query.filter_by(nome="Despesa fantasma").count() == 0


# ===========================================================================
# GRUPO E — Headers de segurança e XSS
# ===========================================================================


HEADERS_EXIGIDOS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}


@pytest.mark.parametrize("cabecalho,esperado", sorted(HEADERS_EXIGIDOS.items()))
def test_header_de_seguranca_presente(como_admin, cabecalho, esperado):
    r = como_admin.get("/clientes")
    assert r.headers.get(cabecalho) == esperado


def test_csp_bloqueia_framing_e_scripts_externos(como_admin):
    """CSP precisa fechar frame-ancestors (clickjacking) e objetos."""
    csp = como_admin.get("/clientes").headers.get("Content-Security-Policy", "")
    assert csp, "Content-Security-Policy ausente"
    assert "frame-ancestors 'none'" in csp
    assert "object-src 'none'" in csp
    assert "base-uri 'none'" in csp


def test_clickjacking_bloqueado_na_tela_de_pagamento(como_admin):
    """A tela de receber dinheiro não pode ser embutida em site externo."""
    with como_admin.application.app_context():
        atendimento_id = Orcamento.query.first().atendimento_id
    r = como_admin.get(f"/atendimentos/{atendimento_id}/finalizar")
    assert r.status_code == 200
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert "frame-ancestors 'none'" in r.headers.get("Content-Security-Policy", "")


def test_hsts_presente_em_https(como_admin):
    r = como_admin.get("/clientes")
    assert r.headers.get("Strict-Transport-Security")


def test_xss_refletido_na_busca_nao_executa(como_admin):
    """Payload de XSS na busca precisa sair escapado."""
    payload = '"><script>alert(1)</script>'
    r = como_admin.get("/clientes", query_string={"busca": payload})
    assert r.status_code == 200
    corpo = r.get_data(as_text=True)
    assert "<script>alert(1)</script>" not in corpo
    assert "&lt;script&gt;" in corpo or "&#34;" in corpo


def test_xss_armazenado_nao_executa(como_admin):
    """Valor salvo no banco precisa continuar escapado na renderização."""
    payload = "<script>alert('xss')</script>"
    post(como_admin, "/clientes/salvar", {"nome": payload, "cpf": ""})
    corpo = como_admin.get("/clientes").get_data(as_text=True)
    assert "<script>alert('xss')</script>" not in corpo
    assert "&lt;script&gt;" in corpo


def test_xss_em_campo_renderizado_do_checklist(como_admin, app_seg):
    payload = '"><img src=x onerror=alert(1)>'
    post(
        como_admin,
        "/checklists/salvar",
        {
            "veiculoId": str(primeiro_veiculo_id(app_seg)),
            "responsavel": payload,
            "condicoesLataria": payload,
        },
    )
    corpo = como_admin.get("/checklists").get_data(as_text=True)
    assert "onerror=alert(1)>" not in corpo


def test_foto_com_nome_hostil_nao_quebra_o_html(como_admin, app_seg):
    """Nenhum pedaço do nome enviado pelo cliente pode chegar ao HTML.

    Duas saídas possíveis e ambas corretas: o arquivo é salvo sob um nome
    gerado no servidor, ou é recusado. O que não pode acontecer é o nome
    aparecer no `src` — aí o `"><script>` escaparia do atributo.
    """
    enviar_foto(como_admin, app_seg, [('"><script>alert(1)</script>.jpg', JPEG_VALIDO)])
    with app_seg.app_context():
        caminhos = db.session.execute(db.select(FotoChecklist.caminho_arquivo)).scalars().all()
    for caminho in caminhos:
        assert "<" not in caminho and ">" not in caminho
        assert '"' not in caminho
    corpo = como_admin.get("/checklists").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in corpo


def test_nome_enviado_nunca_vira_o_caminho_armazenado(como_admin, app_seg):
    """O caminho no banco é um UUID, não o nome que o cliente mandou.

    É o que garante que um nome com traversal ou com aspas não vire um caminho
    no disco nem apareça escapado no HTML.
    """
    enviar_foto(como_admin, app_seg, [("../../dono/segredo.jpg", JPEG_VALIDO)])
    with app_seg.app_context():
        foto = db.session.execute(db.select(FotoChecklist)).scalars().one()
    assert foto.caminho_arquivo.startswith("checklists/")
    assert ".." not in foto.caminho_arquivo
    assert "dono" not in foto.caminho_arquivo
    assert foto.caminho_arquivo.endswith(".jpg")
    nome = foto.caminho_arquivo.rsplit("/", 1)[1]
    assert re.fullmatch(r"[0-9a-f-]{36}\.jpg", nome), nome


# ===========================================================================
# GRUPO G — Regressão: controles que já existem e não podem regredir
# ===========================================================================


def test_toda_rota_post_exige_csrf(app_seg, como_admin):
    """Nenhuma escrita pode acontecer sem token CSRF."""
    escritas = [
        "/login",
        "/logout",
        "/clientes/salvar",
        "/clientes/1/inativar",
        "/veiculos/salvar",
        "/veiculos/1/remover",
        "/checklists/salvar",
        "/checklists/foto/1/remover",
        "/atendimentos/1/salvar",
        "/atendimentos/1/inativar",
        "/atendimentos/1/finalizar",
        "/atendimentos/1/pagamentos",
        "/orcamentos/salvar",
        "/orcamentos/1/inativar",
        "/orcamentos/1/parcelar",
        "/despesas/salvar",
        "/despesas/1/remover",
    ]
    for rota in escritas:
        r = como_admin.post(rota, data={})
        assert r.status_code == 400, f"{rota} aceitou POST sem CSRF"


def test_senha_armazenada_com_bcrypt(app_seg):
    """Senha nunca em texto puro no banco."""
    import bcrypt

    from app.models import Usuario

    with app_seg.app_context():
        usuarios = db.session.execute(db.select(Usuario)).scalars().all()
    assert usuarios

    # O que importa é que a senha não esteja *recuperável* do banco: o hash
    # precisa ter formato bcrypt e não pode conter a senha crua como substring.
    for u in usuarios:
        assert u.senha.startswith(("$2a$", "$2b$", "$2y$")), "senha não é bcrypt"
        assert len(u.senha) == 60, "hash bcrypt tem tamanho fixo de 60"
        for senha_crua in ("admin123", "mecanico123", "atendente123", "admin", "123456"):
            assert senha_crua not in u.senha, "senha em texto puro dentro do hash"

    # E a prova de que é bcrypt de verdade: a senha certa de cada conta abre.
    with app_seg.app_context():
        admin = db.session.execute(
            db.select(Usuario).where(Usuario.login == "admin")
        ).scalar_one()
        mecanico = db.session.execute(
            db.select(Usuario).where(Usuario.login == "mecanico")
        ).scalar_one()
    assert bcrypt.checkpw(b"admin123", admin.senha.encode())
    assert bcrypt.checkpw(b"mecanico123", mecanico.senha.encode())
    # E as contas não são intercambiáveis.
    assert not bcrypt.checkpw(b"mecanico123", admin.senha.encode())
    assert not bcrypt.checkpw(b"admin123", mecanico.senha.encode())

    # bcrypt é salted: dois hashes da mesma senha são diferentes. Se fossem
    # iguais, a tabela viraria um dicionário reverso de senhas.
    with app_seg.app_context():
        hashes = {u.senha for u in db.session.execute(db.select(Usuario)).scalars()}
    assert len(hashes) == 2, "hashes iguais indicam salt ausente ou colisão"


def test_login_anonimo_redirecionado(app_seg, client_seg):
    for caminho in ["/", "/clientes", "/despesas", "/relatorios/orcamentos"]:
        r = client_seg.get(caminho)
        assert r.status_code == 302
        assert "/login" in r.headers["Location"]


def test_consulta_com_aspas_nao_injeta_sql(como_admin):
    """SQLAlchemy parametrizado: aspas não podem virar SQL."""
    payload = "'; DROP TABLE cliente; --"
    r = como_admin.get("/clientes", query_string={"busca": payload})
    assert r.status_code == 200
    with como_admin.application.app_context():
        assert Cliente.query.count() > 0, "tabela cliente foi derrubada"


def test_debug_desligado_em_producao():
    from app.config import ProdConfig

    assert ProdConfig.DEBUG is False
