from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.models import Cliente, Veiculo
from app.routes import guardar_form, recuperar_form
from app.services.cliente_service import cliente_service
from app.services.veiculo_service import veiculo_service

bp = Blueprint("veiculos", __name__, url_prefix="/veiculos")


@bp.get("")
def listar():
    busca = request.args.get("busca", "")
    veiculos = veiculo_service.buscar(busca)
    return render_template(
        "veiculos/lista.html",
        veiculos=veiculos,
        busca=busca,
        pageTitle="Veículos",
        activePage="veiculos",
    )


@bp.get("/novo")
def novo():
    dados = recuperar_form("veiculo_form")
    veiculo = Veiculo()
    veiculo.cliente = Cliente()
    if dados:
        veiculo.id = dados.get("id")
        veiculo.placa = dados.get("placa", "")
        veiculo.marca = dados.get("marca", "")
        veiculo.modelo = dados.get("modelo", "")
        try:
            veiculo.ano = int(dados.get("ano")) if dados.get("ano") else None
        except ValueError:
            veiculo.ano = None
        veiculo.cor = dados.get("cor", "")
        veiculo.cliente.id = dados.get("cliente_id")
    return render_template(
        "veiculos/form.html",
        veiculo=veiculo,
        clientes=cliente_service.listar_ativos(),
        pageTitle="Novo Veículo",
    )


@bp.get("/<int:id>/editar")
def editar(id):
    veiculo = veiculo_service.buscar_por_id(id)
    if veiculo is None:
        flash("Veículo não encontrado", "error")
        return redirect(url_for("veiculos.listar"))
    return render_template(
        "veiculos/form.html",
        veiculo=veiculo,
        clientes=cliente_service.listar_ativos(),
        pageTitle="Editar Veículo",
    )


@bp.post("/salvar")
def salvar():
    form = request.form
    veiculo = Veiculo()
    try:
        veiculo.id = int(form.get("id")) if form.get("id") else None
    except ValueError:
        veiculo.id = None
    veiculo.placa = form.get("placa", "")
    veiculo.marca = form.get("marca", "")
    veiculo.modelo = form.get("modelo", "")
    try:
        veiculo.ano = int(form.get("ano")) if form.get("ano") else None
    except ValueError:
        veiculo.ano = None
    veiculo.cor = form.get("cor", "")
    try:
        cliente_id = int(form.get("cliente.id")) if form.get("cliente.id") else None
    except ValueError:
        cliente_id = None
    veiculo.cliente = Cliente(id=cliente_id)

    if (
        not veiculo.placa.strip()
        or not veiculo.marca.strip()
        or not veiculo.modelo.strip()
        or veiculo.cliente.id is None
    ):
        flash("Preencha placa, marca, modelo e selecione o cliente.", "error")
        return redirect(url_for("veiculos.novo"))
    if veiculo_service.placa_ja_cadastrada(veiculo.placa, veiculo.id):
        flash("Já existe um veículo com esta placa.", "error")
        guardar_form(
            "veiculo_form",
            {
                "id": veiculo.id,
                "placa": veiculo.placa,
                "marca": veiculo.marca,
                "modelo": veiculo.modelo,
                "ano": veiculo.ano,
                "cor": veiculo.cor,
                "cliente_id": veiculo.cliente.id,
            },
        )
        return redirect(url_for("veiculos.novo"))
    veiculo_service.salvar(veiculo)
    flash("Veículo salvo com sucesso.", "success")
    return redirect(url_for("veiculos.listar"))


@bp.post("/<int:id>/remover")
def remover(id):
    if veiculo_service.remover(id):
        flash("Veículo removido.", "success")
    else:
        flash(
            "Veículo possui serviços registrados e não pode ser removido.",
            "error",
        )
    return redirect(url_for("veiculos.listar"))