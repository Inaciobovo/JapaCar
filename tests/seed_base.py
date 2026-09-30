from datetime import datetime

from app.cli import gerar_hash
from app.extensions import db
from app.models import (
    Atendimento,
    ChecklistEntrada,
    Cliente,
    Despesa,
    ItemServico,
    Orcamento,
    Usuario,
    Veiculo,
)

# Credenciais usadas só pelos testes, contra um banco descartável criado em
# tmp_path. São propositalmente fracas porque o objetivo é a ergonomia do
# fixture (`login` faz login direto), não testar força de senha — isso é feito
# em test_security.py. Nenhum destes usuários nunca toca um banco real: o
# `flask usuario-criar` de produção é outro caminho e rejeita estas senhas via
# `senha_forte`.
USUARIOS_TESTE = (
    ("Administrador", "admin", "admin123", "ADMIN"),
    ("Mecânico", "mecanico", "mecanico123", "MECANICO"),
)


def seed_usuarios_teste(app):
    """Cria os usuários que os fixtures de login usam.

    Antes a suíte copiava o `japacar.db` da raiz só para trazer estes dois
    registros. Como `*.db` está no .gitignore, o arquivo não existe em um clone
    limpo e a suíte inteira quebrava com FileNotFoundError. O schema já é
    criado por `db.create_all()` dentro de `create_app`, então o que faltava
    eram só os usuários — e eles são criados aqui.

    Idempotente: não recria se o login já existir.
    """
    with app.app_context():
        for nome, login, senha, perfil in USUARIOS_TESTE:
            if (
                db.session.execute(
                    db.select(Usuario).where(Usuario.login == login)
                ).scalar_one_or_none()
                is not None
            ):
                continue
            db.session.add(
                Usuario(
                    nome=nome,
                    login=login,
                    senha=gerar_hash(senha),
                    perfil=perfil,
                    ativo=True,
                )
            )
        db.session.commit()


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