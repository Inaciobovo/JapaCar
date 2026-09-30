from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.models import ItemServico, Orcamento
from app.routes import guardar_form, recuperar_form
from app.services.atendimento_service import atendimento_service
from app.services.orcamento_service import orcamento_service
from app.utils import parse_valor, parse_valor_zero, valor_valido

bp = Blueprint("orcamentos", __name__, url_prefix="/orcamentos")

STATUS_VALIDOS = {"PENDENTE", "APROVADO", "REJEITADO", "CONCLUIDO", "INATIVO"}


@bp.get("")
def listar():
    status = request.args.get("status", "")
    status_filtro = status if status in STATUS_VALIDOS else None
    if status_filtro:
        orcamentos = orcamento_service.listar_por_status(status_filtro)
    else:
        orcamentos = orcamento_service.listar_todos()
    return render_template(
        "orcamentos/lista.html",
        orcamentos=orcamentos,
        statusFiltro=status_filtro,
        pageTitle="Orçamentos",
        activePage="orcamentos",
    )


@bp.get("/novo")
def novo():
    atendimento_id = request.args.get("atendimentoId", type=int)
    dados = recuperar_form("orcamento_form")
    orcamento = Orcamento()
    orcamento.itens = []
    if dados:
        orcamento.id = dados.get("id")
        orcamento.status = dados.get("status")
        orcamento.observacoes = dados.get("observacoes")
        orcamento.valor_mao_de_obra = dados.get("valor_mao_de_obra")
        for d in dados.get("itens", []):
            item = ItemServico()
            item.descricao = d.get("descricao", "")
            item.quantidade = d.get("quantidade", 1)
            item.valor_unitario = d.get("valor_unitario")
            orcamento.itens.append(item)
        if dados.get("atendimento_id"):
            atendimento_id = dados.get("atendimento_id")
    if not orcamento.itens:
        orcamento.itens.append(ItemServico())
    if atendimento_id and orcamento.atendimento_id is None:
        atendimento = atendimento_service.buscar_por_id(atendimento_id)
        orcamento.atendimento = atendimento
    return render_template(
        "orcamentos/form.html",
        orcamento=orcamento,
        atendimentos=atendimento_service.listar_todos(),
        pageTitle="Novo Orçamento",
        activePage="orcamentos",
    )


@bp.get("/<int:id>/editar")
def editar(id):
    orcamento = orcamento_service.buscar_por_id(id)
    if orcamento is None:
        flash("Orçamento não encontrado", "error")
        return redirect(url_for("orcamentos.listar"))
    return render_template(
        "orcamentos/form.html",
        orcamento=orcamento,
        atendimentos=atendimento_service.listar_todos(),
        pageTitle=f"Editar Orçamento #{id}",
        activePage="orcamentos",
    )


@bp.post("/salvar")
def salvar():
    form = request.form

    try:
        orcamento_id = int(form.get("id")) if form.get("id") else None
    except ValueError:
        orcamento_id = None
    atendimento_id = form.get("atendimentoId", type=int)

    if atendimento_id is None:
        flash("Selecione o atendimento/serviço.", "error")
        return redirect(url_for("orcamentos.novo"))
    atendimento = atendimento_service.buscar_por_id(atendimento_id)
    if atendimento is None:
        flash("Atendimento não encontrado.", "error")
        return redirect(url_for("orcamentos.novo"))

    orcamento = Orcamento()
    orcamento.id = orcamento_id
    orcamento.atendimento = atendimento

    # `status` chega do formulário e antes era gravado cru. Um valor fora da
    # lista Some do relatório e quebra a lógica de "orçamento em aberto",
    # sem deixar rastro de que houve erro.
    status = (form.get("status") or "").strip()
    if status and status not in STATUS_VALIDOS:
        flash("Status de orçamento inválido.", "error")
        return redirect(url_for("orcamentos.novo", atendimentoId=atendimento_id))
    orcamento.status = status or "PENDENTE"

    orcamento.observacoes = form.get("observacoes") or None

    mao_de_obra = parse_valor(form.get("valorMaoDeObraText")) or parse_valor_zero("0")
    if not valor_valido(mao_de_obra):
        flash("Valor de mão de obra inválido.", "error")
        return redirect(url_for("orcamentos.novo", atendimentoId=atendimento_id))
    orcamento.valor_mao_de_obra = mao_de_obra

    descricoes = form.getlist("itemDescricao")
    quantidades = form.getlist("itemQuantidade")
    valores = form.getlist("itemValorUnitario")

    itens = []
    for i, descricao in enumerate(descricoes):
        if not descricao or not descricao.strip():
            continue
        item = ItemServico()
        item.orcamento = orcamento
        item.descricao = descricao.strip()

        try:
            quantidade = (
                int(quantidades[i]) if i < len(quantidades) and quantidades[i] else 1
            )
        except (TypeError, ValueError):
            quantidade = 1
        if quantidade < 1 or quantidade > 9999:
            flash("Quantidade de item inválida.", "error")
            return redirect(url_for("orcamentos.novo", atendimentoId=atendimento_id))
        item.quantidade = quantidade

        valor_unitario = (
            parse_valor(valores[i]) if i < len(valores) else None
        )
        if valor_unitario is None:
            valor_unitario = parse_valor_zero("0")
        if not valor_valido(valor_unitario):
            flash("Valor unitário de item inválido.", "error")
            return redirect(url_for("orcamentos.novo", atendimentoId=atendimento_id))
        item.valor_unitario = valor_unitario
        itens.append(item)

    if not itens:
        flash("Adicione ao menos um item ao orçamento.", "error")
        guardar_form(
            "orcamento_form",
            {
                "id": orcamento_id,
                "status": orcamento.status,
                "observacoes": orcamento.observacoes,
                "valor_mao_de_obra": orcamento.valor_mao_de_obra,
                "atendimento_id": atendimento_id,
                "itens": [
                    {
                        "descricao": d,
                        "quantidade": int(q) if q and q.isdigit() else 1,
                        "valor_unitario": parse_valor_zero(v) if v else None,
                    }
                    for d, q, v in zip(descricoes, quantidades, valores)
                    if d and d.strip()
                ],
            },
        )
        return redirect(url_for("orcamentos.novo", atendimentoId=atendimento_id))

    orcamento.itens = itens
    orcamento_service.salvar(orcamento)
    flash("Orçamento salvo com sucesso.", "success")
    return redirect(url_for("atendimentos.detalhe", id=atendimento.id))


@bp.post("/<int:id>/inativar")
def inativar(id):
    orcamento = orcamento_service.buscar_por_id(id)
    atendimento_id = orcamento.atendimento.id if orcamento is not None else None
    orcamento_service.inativar(id)
    flash("Orçamento inativado.", "success")
    return redirect(url_for("atendimentos.detalhe", id=atendimento_id))


@bp.post("/<int:id>/parcelar")
def parcelar(id):
    orcamento = orcamento_service.buscar_por_id(id)
    if orcamento is None:
        flash("Orçamento não encontrado", "error")
        return redirect(url_for("orcamentos.listar"))
    quantidade = request.form.get("quantidadeParcelas")
    _, erro = orcamento_service.gerar_parcelas(id, quantidade)
    if erro:
        flash(erro, "error")
    else:
        flash(f"Plano de parcelamento gerado para o orçamento #{id}.", "success")
    return redirect(url_for("atendimentos.finalizar", id=orcamento.atendimento_id))


@bp.get("/<int:id>/pdf")
def pdf(id):
    orcamento = orcamento_service.buscar_por_id(id)
    if orcamento is None:
        return "", 404
    from app.pdf.orcamento_pdf import gerar_pdf

    pdf_bytes = gerar_pdf(orcamento)
    from flask import Response
    from urllib.parse import quote

    filename = f"orcamento-{id}.pdf"
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}; filename*=UTF-8''{quote(filename)}"
        },
    )