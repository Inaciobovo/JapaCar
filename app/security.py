"""Controle de acesso por perfil.

O campo `Usuario.perfil` existia no modelo desde a migracao do Spring Boot, mas
nada no sistema consultava o valor: qualquer conta logada fazia tudo, inclusive
ver receita e despesa da oficina. Aqui fica a politica unica, aplicada por
decorator nas rotas, para nao depender de esconder botao no menu.

Regra definida pelo cliente: o perfil MECANICO monta orcamento e acompanha o
servico, mas nao enxerga a parte financeira (quanto entra e quanto sai).
"""

from functools import wraps

from flask import abort, render_template, request
from flask_login import current_user

ADMIN = "ADMIN"
MECANICO = "MECANICO"
ATENDENTE = "ATENDENTE"

PERFIS_VALIDOS = frozenset({ADMIN, MECANICO, ATENDENTE})

# Quem enxerga receita, despesa e saldo consolidado.
PERFIS_FINANCEIROS = frozenset({ADMIN})


def eh_financeiro(usuario=None):
    usuario = usuario or current_user
    return getattr(usuario, "perfil", None) in PERFIS_FINANCEIROS


def perfil_efetivo():
    """Perfil do usuario logado, ou None.

    Uma conta com perfil desconhecido (valor gravado fora da lista) e tratada
    como sem privilegio: falha fechada.
    """
    if not current_user.is_authenticated:
        return None
    perfil = getattr(current_user, "perfil", None)
    return perfil if perfil in PERFIS_VALIDOS else None


def _sem_permissao():
    """Resposta padronizada para acesso negado.

    Navegador recebe 403 com a pagina; chamada de API/POST recebe 403 seco.
    """
    if request.accept_mimetypes.best == "application/json":
        abort(403)
    return (
        render_template(
            "erro_acesso.html",
            pageTitle="Acesso negado",
        ),
        403,
    )


def requer_financeiro(view):
    """Restringe a rota aos perfis que podem ver o Consolidado."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        if not eh_financeiro():
            return _sem_permissao()
        return view(*args, **kwargs)

    return wrapper
