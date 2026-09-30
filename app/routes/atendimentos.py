from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.models import Atendimento
from app.services.atendimento_service import atendimento_service
from app.services.orcamento_service import orcamento_service
from app.services.veiculo_service import veiculo_service

bp = Blueprint("atendimentos", __name__, url_prefix="/atendimentos")

STATUS_VALIDOS = {"EM_ANDAMENTO", "CONCLUIDO", "CANCELADO"}


@bp.get("")
def listar():
    status = request.args.get("status", "")
    status_filtro = status if status in STATUS_VALIDOS else None
    if status_filtro:
        atendimentos = atendimento_service.listar_por_status(status_filtro)
    else:
        atendimentos = atendimento_service.listar_todos()
    return render_template(
        "atendimentos/lista.html",
        atendimentos=atendimentos,
        statusFiltro=status_filtro,
        pageTitle="Painel de Serviços",
        activePage="atendimentos",
    )


@bp.get("/<int:id>")
def detalhe(id):
    atendimento = atendimento_service.buscar_por_id(id)
    if atendimento is None:
        flash("Atendimento não encontrado", "error")
        return redirect(url_for("atendimentos.listar"))
    return render_template(
        "atendimentos/detalhe.html",
        atendimento=atendimento,
        orcamentos=orcamento_service.listar_por_atendimento(id),
        pageTitle=f"Serviço #{id}",
        activePage="atendimentos",
    )


@bp.get("/<int:id>/editar")
def editar(id):
    atendimento = atendimento_service.buscar_por_id(id)
    if atendimento is None:
        flash("Atendimento não encontrado", "error")
        return redirect(url_for("atendimentos.listar"))
    return render_template(
        "atendimentos/form.html",
        atendimento=atendimento,
        veiculos=veiculo_service.listar_todos(),
        pageTitle=f"Editar Serviço #{id}",
        activePage="atendimentos",
    )


@bp.post("/<int:id>/salvar")
def salvar(id):
    atendimento = atendimento_service.buscar_por_id(id)
    if atendimento is None:
        flash("Atendimento não encontrado", "error")
        return redirect(url_for("atendimentos.listar"))
    veiculo_id = request.form.get("veiculoId")
    if veiculo_id:
        veiculo = veiculo_service.buscar_por_id(int(veiculo_id))
        if veiculo is not None:
            atendimento.veiculo = veiculo
    atendimento.mecanico_responsavel = request.form.get("mecanicoResponsavel") or None
    atendimento.conferente = request.form.get("conferente") or None
    atendimento.observacoes = request.form.get("observacoes") or None
    atendimento_service.salvar(atendimento)
    flash("Serviço atualizado com sucesso.", "success")
    return redirect(url_for("atendimentos.detalhe", id=atendimento.id))


@bp.post("/<int:id>/inativar")
def inativar(id):
    atendimento_service.inativar(id)
    flash("Serviço inativado (status cancelado).", "success")
    return redirect(url_for("atendimentos.listar"))


@bp.get("/<int:id>/finalizar")
def finalizar(id):
    atendimento = atendimento_service.buscar_por_id(id)
    if atendimento is None:
        flash("Atendimento não encontrado", "error")
        return redirect(url_for("atendimentos.listar"))
    return render_template(
        "atendimentos/finalizar.html",
        atendimento=atendimento,
        orcamentos=orcamento_service.listar_por_atendimento(id),
        acaoFinalizar=url_for("atendimentos.finalizar_post", id=id),
        acaoPagamentos=url_for("atendimentos.pagamentos_post", id=id),
        pageTitle=f"Finalizar Serviço #{id}",
        activePage="atendimentos",
    )


def _pagamentos_from_form():
    ids = request.form.getlist("pagamentoOrcamentoId")
    situacoes = request.form.getlist("pagamentoSituacao")
    formas = request.form.getlist("pagamentoForma")
    valores = request.form.getlist("pagamentoValor")
    datas = request.form.getlist("pagamentoData")
    ids_conv = []
    for x in ids:
        try:
            ids_conv.append(int(x))
        except ValueError:
            ids_conv.append(None)
    return ids_conv, situacoes, formas, valores, datas


@bp.post("/<int:id>/finalizar")
def finalizar_post(id):
    if atendimento_service.buscar_por_id(id) is None:
        flash("Atendimento não encontrado", "error")
        return redirect(url_for("atendimentos.listar"))
    _aplicar_pagamentos()
    atendimento_service.finalizar(id)
    flash("Serviço finalizado e pagamentos registrados.", "success")
    return redirect(url_for("atendimentos.detalhe", id=id))


@bp.post("/<int:id>/pagamentos")
def pagamentos_post(id):
    if atendimento_service.buscar_por_id(id) is None:
        flash("Atendimento não encontrado", "error")
        return redirect(url_for("atendimentos.listar"))
    _aplicar_pagamentos()
    flash("Pagamentos registrados com sucesso.", "success")
    return redirect(url_for("atendimentos.detalhe", id=id))


def _aplicar_pagamentos():
    ids, situacoes, formas, valores, datas = _pagamentos_from_form()
    orcamento_service.aplicar_pagamentos(ids, situacoes, formas, valores, datas)
    _aplicar_pagamentos_parcelas()


def _pagamentos_parcelas_from_form():
    ids = request.form.getlist("parcelaId")
    situacoes = request.form.getlist("parcelaSituacao")
    formas = request.form.getlist("parcelaForma")
    valores = request.form.getlist("parcelaValor")
    datas = request.form.getlist("parcelaData")
    ids_conv = []
    for x in ids:
        try:
            ids_conv.append(int(x))
        except ValueError:
            ids_conv.append(None)
    return ids_conv, situacoes, formas, valores, datas


def _aplicar_pagamentos_parcelas():
    ids, situacoes, formas, valores, datas = _pagamentos_parcelas_from_form()
    orcamento_service.aplicar_pagamentos_parcelas(
        ids, situacoes, formas, valores, datas
    )