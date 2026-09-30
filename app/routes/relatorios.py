from datetime import date, datetime, time
from decimal import Decimal

from flask import Blueprint, flash, render_template, request

from app.models import BR_TZ, STATUS_ORCAMENTO_DESCRICOES, Orcamento, _dec
from app.security import requer_financeiro

bp = Blueprint("relatorios", __name__, url_prefix="/relatorios")


@bp.get("/orcamentos")
@requer_financeiro
def orcamentos():
    data_inicio = request.args.get("dataInicio", "") or ""
    data_fim = request.args.get("dataFim", "") or ""
    status = request.args.get("status", "") or ""

    query = Orcamento.query
    if data_inicio and data_fim:
        try:
            inicio = datetime.combine(
                date.fromisoformat(data_inicio), time.min, tzinfo=BR_TZ
            )
            fim = datetime.combine(date.fromisoformat(data_fim), time.max, tzinfo=BR_TZ)
            query = query.filter(Orcamento.data_criacao.between(inicio, fim))
        except ValueError:
            flash("Datas inválidas no filtro do relatório.", "error")
            data_inicio = ""
            data_fim = ""
    if status:
        # Um status fora da lista faz o filtro devolver zero orçamentos sem
        # explicar o motivo; melhor ignorá-lo e mostrar tudo.
        if status in STATUS_ORCAMENTO_DESCRICOES:
            query = query.filter(Orcamento.status == status)
        else:
            status = ""

    orcamentos = query.order_by(Orcamento.data_criacao.desc()).all()

    resumo = {
        "total": len(orcamentos),
        "valor_total": sum((_dec(o.valor_total) for o in orcamentos), Decimal("0")),
        "valor_pecas": sum((_dec(o.valor_pecas) for o in orcamentos), Decimal("0")),
        "valor_mao_de_obra": sum(
            (_dec(o.valor_mao_de_obra) for o in orcamentos), Decimal("0")
        ),
        "valor_pago": sum((_dec(o.valor_pago) for o in orcamentos), Decimal("0")),
        "pagos": sum(1 for o in orcamentos if o.status_pagamento == "PAGO"),
    }

    return render_template(
        "relatorios/orcamentos.html",
        orcamentos=orcamentos,
        resumo=resumo,
        dataInicio=data_inicio,
        dataFim=data_fim,
        statusFiltro=status or None,
        pageTitle="Relatório de Orçamentos",
        activePage="relatorios",
    )