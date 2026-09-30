from datetime import datetime

from app.extensions import db
from app.models import (
    Atendimento,
    ChecklistEntrada,
    Cliente,
    Despesa,
    ItemServico,
    Orcamento,
    Veiculo,
)


def seed_dados_base(app):
    """Popula o banco do app de teste com um dataset mínimo para a suíte.

    É idempotente: não faz nada se já existirem clientes.
    """
    with app.app_context():
        if Cliente.query.count() > 0:
            return
        cliente = Cliente(
            nome="Cliente Base",
            cpf="52998224725",
            telefone="(11) 91111-1111",
            email="base@example.com",
            endereco="Rua Base, 1",
        )
        db.session.add(cliente)
        db.session.flush()

        veiculo = Veiculo(
            placa="BASE-0001",
            marca="Fiat",
            modelo="Uno",
            ano=2015,
            cor="Branco",
            cliente_id=cliente.id,
        )
        db.session.add(veiculo)
        db.session.flush()

        checklist = ChecklistEntrada(
            veiculo_id=veiculo.id,
            quilometragem=1000,
            nivel_combustivel="METADE",
            responsavel="Mecânico",
        )
        db.session.add(checklist)
        db.session.flush()

        at = Atendimento(
            veiculo_id=veiculo.id,
            checklist_entrada_id=checklist.id,
            status="EM_ANDAMENTO",
            data_entrada=datetime.now(),
            mecanico_responsavel="Mecânico",
        )
        db.session.add(at)
        db.session.flush()

        orc = Orcamento(
            atendimento_id=at.id,
            status="PENDENTE",
            status_pagamento="PENDENTE",
            valor_mao_de_obra=50,
            valor_pecas=30,
            valor_total=80,
        )
        db.session.add(orc)
        db.session.flush()

        item = ItemServico(
            orcamento_id=orc.id,
            descricao="Serviço base",
            quantidade=1,
            valor_unitario=30,
        )
        db.session.add(item)

        despesa = Despesa(
            descricao="Despesa base",
            valor=20.5,
            data=datetime.now().date(),
            categoria="OUTROS",
        )
        db.session.add(despesa)
        db.session.commit()