from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.models import Cliente
from app.routes import guardar_form, recuperar_form
from app.services.cliente_service import cliente_service
from app.utils import cpf_valido

bp = Blueprint("clientes", __name__, url_prefix="/clientes")


@bp.get("")
def listar():
    busca = request.args.get("busca", "")
    clientes = cliente_service.buscar(busca)
    return render_template(
        "clientes/lista.html",
        clientes=clientes,
        busca=busca,
        pageTitle="Clientes",
        activePage="clientes",
    )


@bp.get("/novo")
def novo():
    dados = recuperar_form("cliente_form")
    cliente = Cliente()
    if dados:
        cliente.id = dados.get("id")
        cliente.nome = dados.get("nome", "")
        cliente.cpf = dados.get("cpf", "")
        cliente.telefone = dados.get("telefone", "")
        cliente.email = dados.get("email", "")
        cliente.endereco = dados.get("endereco", "")
    return render_template(
        "clientes/form.html", cliente=cliente, pageTitle="Novo Cliente"
    )


@bp.get("/<int:id>/editar")
def editar(id):
    cliente = cliente_service.buscar_por_id(id)
    if cliente is None:
        flash("Cliente não encontrado", "error")
        return redirect(url_for("clientes.listar"))
    return render_template(
        "clientes/form.html", cliente=cliente, pageTitle="Editar Cliente"
    )


@bp.post("/salvar")
def salvar():
    form = request.form
    cliente = Cliente()
    try:
        cliente.id = int(form.get("id")) if form.get("id") else None
    except ValueError:
        cliente.id = None
    cliente.nome = form.get("nome", "")
    cliente.cpf = form.get("cpf") or None
    cliente.telefone = form.get("telefone") or None
    cliente.email = form.get("email") or None
    cliente.endereco = form.get("endereco") or None

    if not cliente.nome or not cliente.nome.strip():
        flash("O nome do cliente é obrigatório.", "error")
        return redirect(url_for("clientes.novo"))
    if cliente.cpf and not cpf_valido(cliente.cpf):
        flash("CPF inválido. Confira os dígitos.", "error")
        return redirect(url_for("clientes.novo"))
    if cliente_service.cpf_ja_cadastrado(cliente.cpf, cliente.id):
        flash("Já existe um cliente com este CPF.", "error")
        guardar_form(
            "cliente_form",
            {
                "id": cliente.id,
                "nome": cliente.nome,
                "cpf": cliente.cpf,
                "telefone": cliente.telefone,
                "email": cliente.email,
                "endereco": cliente.endereco,
            },
        )
        return redirect(url_for("clientes.novo"))
    cliente_service.salvar(cliente)
    flash("Cliente salvo com sucesso.", "success")
    return redirect(url_for("clientes.listar"))


@bp.post("/<int:id>/inativar")
def inativar(id):
    cliente_service.inativar(id)
    flash("Cliente inativado.", "success")
    return redirect(url_for("clientes.listar"))