from decimal import Decimal

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.models import CATEGORIA_DESCRICOES, Despesa
from app.security import requer_financeiro
from app.services.despesa_service import despesa_service
from app.utils import parse_valor, valor_valido

bp = Blueprint("despesas", __name__, url_prefix="/despesas")

CATEGORIAS = list(CATEGORIA_DESCRICOES.items())


@bp.get("")
@requer_financeiro
def listar():
    data_inicio = request.args.get("dataInicio", "") or ""
    data_fim = request.args.get("dataFim", "") or ""
    categoria = request.args.get("categoria", "") or ""
    despesas = despesa_service.buscar(data_inicio, data_fim, categoria)
    return render_template(
        "despesas/lista.html",
        despesas=despesas,
        categorias=CATEGORIAS,
        dataInicio=data_inicio,
        dataFim=data_fim,
        categoria=categoria,
        pageTitle="Despesas",
        activePage="despesas",
    )


@bp.get("/nova")
@requer_financeiro
def nova():
    return render_template(
        "despesas/form.html",
        despesa=Despesa(),
        categorias=CATEGORIAS,
        pageTitle="Nova Despesa",
        activePage="despesas",
    )


@bp.get("/<int:id>/editar")
@requer_financeiro
def editar(id):
    despesa = despesa_service.buscar_por_id(id)
    if despesa is None:
        flash("Despesa não encontrada", "error")
        return redirect(url_for("despesas.listar"))
    return render_template(
        "despesas/form.html",
        despesa=despesa,
        categorias=CATEGORIAS,
        pageTitle="Editar Despesa",
        activePage="despesas",
    )


@bp.post("/salvar")
@requer_financeiro
def salvar():
    form = request.form
    despesa = Despesa()
    try:
        despesa.id = int(form.get("id")) if form.get("id") else None
    except ValueError:
        despesa.id = None
    despesa.descricao = form.get("descricao", "")
    # Categoria vai para o agrupamento do dashboard e do relatório; um valor
    # fora da lista some do gráfico sem aviso.
    categoria = (form.get("categoria") or "").strip()
    if categoria and categoria not in CATEGORIA_DESCRICOES:
        flash("Categoria de despesa inválida.", "error")
        return redirect(url_for("despesas.nova"))
    despesa.categoria = categoria or None
    despesa.observacoes = form.get("observacoes") or None
    despesa.data = _parse_data_form(form.get("data"))
    despesa.valor = parse_valor(form.get("valorText"))

    if (
        not despesa.descricao.strip()
        or despesa.valor is None
        or despesa.data is None
    ):
        flash("Descrição, valor e data são obrigatórios.", "error")
        return redirect(url_for("despesas.nova"))
    # Despesa é dinheiro que sai: zero e negativo não fazem sentido.
    if not valor_valido(despesa.valor, minimo=Decimal("0.01")):
        flash("O valor da despesa deve estar entre 0,01 e 99.999.999,99.", "error")
        return redirect(url_for("despesas.nova"))

    despesa_service.salvar(despesa)
    flash("Despesa salva com sucesso.", "success")
    return redirect(url_for("despesas.listar"))


def _parse_data_form(valor):
    if not valor or not valor.strip():
        return None
    from datetime import datetime

    texto = valor.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto, fmt).date()
        except ValueError:
            continue
    return None


@bp.post("/<int:id>/remover")
@requer_financeiro
def remover(id):
    despesa_service.remover(id)
    flash("Despesa removida.", "success")
    return redirect(url_for("despesas.listar"))