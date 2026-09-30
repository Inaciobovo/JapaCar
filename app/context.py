from datetime import date

from flask import request

from app.security import eh_financeiro, perfil_efetivo
from app.utils import active_page_for, eh_dispositivo_movel

from .models import (
    CATEGORIA_DESCRICOES,
    FORMA_PAGAMENTO_DESCRICOES,
    NIVEL_COMBUSTIVEL_DESCRICOES,
    STATUS_ATENDIMENTO_DESCRICOES,
    STATUS_ORCAMENTO_DESCRICOES,
    STATUS_PAGAMENTO_DESCRICOES,
)


def inject_globals():
    is_mobile = eh_dispositivo_movel(request.headers.get("User-Agent"))
    return {
        "activePage": active_page_for(request.path),
        "isMobile": is_mobile,
        "deviceClass": "device-mobile" if is_mobile else "device-desktop",
        "appName": "JAPACAR",
        "hojeIso": date.today().isoformat(),
        "podeVerFinanceiro": eh_financeiro(),
        "perfilAtual": perfil_efetivo(),
    }


def inject_enums():
    return {
        "STATUS_ATENDIMENTO": list(STATUS_ATENDIMENTO_DESCRICOES.items()),
        "STATUS_ORCAMENTO": list(STATUS_ORCAMENTO_DESCRICOES.items()),
        "STATUS_PAGAMENTO": list(STATUS_PAGAMENTO_DESCRICOES.items()),
        "FORMA_PAGAMENTO": list(FORMA_PAGAMENTO_DESCRICOES.items()),
        "NIVEL_COMBUSTIVEL": list(NIVEL_COMBUSTIVEL_DESCRICOES.items()),
        "CATEGORIA_DESPESA": list(CATEGORIA_DESCRICOES.items()),
    }