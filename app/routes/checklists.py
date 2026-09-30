from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.models import NIVEL_COMBUSTIVEL_DESCRICOES, ChecklistEntrada
from app.services.checklist_service import checklist_service
from app.services.file_storage_service import UploadRejeitado
from app.services.veiculo_service import veiculo_service

bp = Blueprint("checklists", __name__, url_prefix="/checklists")


@bp.get("")
def listar():
    veiculo_id = request.args.get("veiculoId", "") or ""
    data_inicio = request.args.get("dataInicio", "") or ""
    data_fim = request.args.get("dataFim", "") or ""
    responsavel = request.args.get("responsavel", "") or ""
    checklists = checklist_service.buscar(veiculo_id, data_inicio, data_fim, responsavel)
    return render_template(
        "checklists/lista.html",
        checklists=checklists,
        veiculoId=veiculo_id,
        dataInicio=data_inicio,
        dataFim=data_fim,
        responsavel=responsavel,
        pageTitle="Checklists",
        activePage="checklists",
    )


@bp.get("/nova")
def nova():
    checklist = ChecklistEntrada()
    checklist.veiculo = None
    return render_template(
        "checklists/form.html",
        checklist=checklist,
        veiculos=veiculo_service.listar_todos(),
        pageTitle="Novo Checklist de Entrada",
        activePage="checklists",
    )


@bp.get("/<int:id>")
def detalhe(id):
    checklist = checklist_service.buscar_por_id(id)
    if checklist is None:
        flash("Checklist não encontrado", "error")
        return redirect(url_for("checklists.listar"))
    return render_template(
        "checklists/detalhe.html",
        checklist=checklist,
        pageTitle=f"Checklist #{id}",
        activePage="checklists",
    )


@bp.get("/<int:id>/editar")
def editar(id):
    checklist = checklist_service.buscar_por_id(id)
    if checklist is None:
        flash("Checklist não encontrado", "error")
        return redirect(url_for("checklists.listar"))
    return render_template(
        "checklists/form.html",
        checklist=checklist,
        veiculos=veiculo_service.listar_todos(),
        pageTitle=f"Editar Checklist #{id}",
        activePage="checklists",
    )


@bp.post("/salvar")
def salvar():
    form = request.form
    try:
        checklist_id = int(form.get("id")) if form.get("id") else None
    except ValueError:
        checklist_id = None
    veiculo_id = form.get("veiculoId", type=int)

    if veiculo_id is None:
        flash("Selecione o veículo.", "error")
        return redirect(url_for("checklists.nova"))
    responsavel = form.get("responsavel") or ""
    if not responsavel.strip():
        flash("Informe o responsável pelo checklist.", "error")
        return redirect(url_for("checklists.nova"))

    checklist = ChecklistEntrada()
    checklist.id = checklist_id
    checklist.veiculo = veiculo_service.buscar_por_id(veiculo_id)
    if checklist.veiculo is None:
        flash("Veículo não encontrado.", "error")
        return redirect(url_for("checklists.nova"))
    checklist.quilometragem = form.get("quilometragem", type=int)
    nivel = (form.get("nivelCombustivel") or "").strip()
    if nivel and nivel not in NIVEL_COMBUSTIVEL_DESCRICOES:
        flash("Nível de combustível inválido.", "error")
        return redirect(url_for("checklists.nova"))
    checklist.nivel_combustivel = nivel or None
    checklist.responsavel = responsavel
    checklist.condicoes_lataria = form.get("condicoesLataria") or None
    checklist.observacoes_gerais = form.get("observacoesGerais") or None

    fotos = [f for f in request.files.getlist("novasFotos") if f and f.filename]
    maximo = current_app.config["UPLOAD_MAX_FILES"]
    if len(fotos) > maximo:
        flash(f"Envie no máximo {maximo} fotos por checklist.", "error")
        return redirect(url_for("checklists.nova" if checklist_id is None else "checklists.editar", id=checklist_id))

    descricoes = request.form.getlist("descricaoFoto")
    descricoes_map = {
        str(i): d for i, d in enumerate(descricoes) if d and d.strip()
    }

    try:
        salvo = checklist_service.salvar(checklist, fotos, descricoes_map)
    except UploadRejeitado as erro:
        # Um arquivo recusado precisa aparecer para o operador como erro.
        # Salvar "com sucesso" apesar de um .html barrado seria o pior dos
        # dois mundos: o operador acredita que a foto foi registrada.
        flash(str(erro), "error")
        return redirect(
            url_for("checklists.nova" if checklist_id is None else "checklists.editar", id=checklist_id)
        )
    if checklist_id is not None:
        flash("Checklist atualizado com sucesso.", "success")
        return redirect(url_for("checklists.detalhe", id=salvo.id))
    flash("Checklist de entrada finalizado. O veículo foi enviado para o painel de serviços.", "success")
    return redirect(url_for("atendimentos.listar"))


@bp.post("/foto/<int:foto_id>/remover")
def remover_foto(foto_id):
    checklist_id = request.form.get("checklistId", type=int)
    checklist_service.remover_foto(foto_id)
    flash("Foto removida.", "success")
    return redirect(url_for("checklists.editar", id=checklist_id))