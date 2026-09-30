from datetime import datetime

from app import create_app
from app.extensions import db
from app.models import (
    Atendimento,
    Cliente,
    Despesa,
    Orcamento,
    Parcela,
    Usuario,
    Veiculo,
)
from app.services.veiculo_service import veiculo_service


def _login(client, usuario="admin", senha="admin123"):
    return client.post("/login", data={"username": usuario, "password": senha})


def test_seed_cria_usuarios_padrao(tmp_path):
    import shutil
    from pathlib import Path

    base = Path(__file__).resolve().parent.parent
    db_copy = tmp_path / "japacar.db"
    shutil.copyfile(base / "japacar.db", db_copy)
    app = create_app(
        "dev",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_copy}",
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SEED_ON_STARTUP=True,
    )
    with app.app_context():
        assert db.session.execute(
            db.select(Usuario).where(Usuario.login == "admin")
        ).scalar_one_or_none() is not None
        assert db.session.execute(
            db.select(Usuario).where(Usuario.login == "mecanico")
        ).scalar_one_or_none() is not None


def test_anonimo_redirecionado_para_login(client):
    r = client.get("/")
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]
    r = client.get("/clientes")
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]


def test_login_sucesso(client):
    r = _login(client)
    assert r.status_code == 302
    assert r.headers["Location"] == "/"


def test_login_senha_invalida(client):
    r = _login(client, senha="errada")
    assert r.status_code == 302
    assert "error=true" in r.headers["Location"]


def test_logout(client):
    _login(client)
    r = client.post("/logout")
    assert r.status_code == 302
    assert "logout=true" in r.headers["Location"]


def test_paginas_autenticado(client):
    _login(client)
    for path in [
        "/",
        "/clientes",
        "/veiculos",
        "/atendimentos",
        "/orcamentos",
        "/checklists",
        "/despesas",
    ]:
        assert client.get(path).status_code == 200, path


def test_paginas_detalhe(client):
    _login(client)
    with client.application.app_context():
        ids = {
            "atendimento": Atendimento.query.first().id,
            "orcamento": Orcamento.query.first().id,
            "checklist": db.session.execute(
                db.select(Atendimento).limit(1)
            ).scalar_one_or_none().id,
            "veiculo": Veiculo.query.first().id,
            "cliente": Cliente.query.first().id,
            "despesa": Despesa.query.first().id,
        }
    paths = [
        f"/atendimentos/{ids['atendimento']}",
        f"/atendimentos/{ids['atendimento']}/editar",
        f"/atendimentos/{ids['atendimento']}/finalizar",
        f"/orcamentos/{ids['orcamento']}/editar",
        f"/veiculos/{ids['veiculo']}/editar",
        f"/clientes/{ids['cliente']}/editar",
        f"/despesas/{ids['despesa']}/editar",
    ]
    for path in paths:
        assert client.get(path).status_code == 200, path


def test_pdf_orcamento(client):
    _login(client)
    with client.application.app_context():
        orc_id = Orcamento.query.first().id
    r = client.get(f"/orcamentos/{orc_id}/pdf")
    assert r.status_code == 200
    assert r.mimetype == "application/pdf"
    assert len(r.data) > 500


def test_criar_cliente(client):
    _login(client)
    r = client.post(
        "/clientes/salvar",
        data={
            "nome": "Cliente Teste",
            "cpf": "111.444.777-35",
            "telefone": "(11) 99999-8888",
            "email": "teste@example.com",
            "endereco": "Rua Teste, 123",
        },
    )
    assert r.status_code == 302
    assert r.headers["Location"] == "/clientes"
    with client.application.app_context():
        assert (
            db.session.execute(db.select(Cliente).where(Cliente.nome == "Cliente Teste"))
            .scalar_one_or_none()
            is not None
        )


def test_cliente_cpf_duplicado_rejeitado(client):
    _login(client)
    with client.application.app_context():
        cpf = Cliente.query.filter(Cliente.cpf.isnot(None)).first().cpf
    r = client.post(
        "/clientes/salvar",
        data={"nome": "Cliente X", "cpf": cpf},
    )
    assert r.status_code == 302
    assert r.headers["Location"] == "/clientes/novo"


def test_criar_veiculo(client):
    _login(client)
    with client.application.app_context():
        cliente_id = Cliente.query.first().id
    r = client.post(
        "/veiculos/salvar",
        data={
            "placa": "XYZ-0000",
            "marca": "Teste",
            "modelo": "Teste 1.0",
            "ano": "2020",
            "cor": "Preto",
            "cliente.id": str(cliente_id),
        },
    )
    assert r.status_code == 302
    assert r.headers["Location"] == "/veiculos"
    with client.application.app_context():
        assert (
            db.session.execute(db.select(Veiculo).where(Veiculo.placa == "XYZ-0000"))
            .scalar_one_or_none()
            is not None
        )


def test_registrar_pagamento(client):
    _login(client)
    with client.application.app_context():
        orc = db.session.execute(
            db.select(Orcamento)
            .where(Orcamento.status_pagamento == "PENDENTE")
            .limit(1)
        ).scalars().first()
        if orc is None:
            orc = Orcamento.query.first()
        orc_id = orc.id
        atendimento_id = orc.atendimento_id
    r = client.post(
        f"/atendimentos/{atendimento_id}/pagamentos",
        data={
            "pagamentoOrcamentoId": [str(orc_id)],
            "pagamentoSituacao": ["PAGO"],
            "pagamentoForma": ["DINHEIRO"],
            "pagamentoValor": ["100,00"],
            "pagamentoData": ["2026-09-21"],
        },
    )
    assert r.status_code == 302
    with client.application.app_context():
        orc = db.session.get(Orcamento, orc_id)
        assert orc.status_pagamento == "PAGO"
        assert orc.forma_pagamento == "DINHEIRO"
        assert orc.valor_pago == 100.00


def test_finalizar_atendimento(client):
    _login(client)
    with client.application.app_context():
        veiculo_id = Veiculo.query.first().id
        at = Atendimento(
            veiculo_id=veiculo_id,
            status="EM_ANDAMENTO",
            data_entrada=datetime.now(),
            mecanico_responsavel="Teste",
        )
        db.session.add(at)
        db.session.commit()
        at_id = at.id
    r = client.post(f"/atendimentos/{at_id}/finalizar", data={})
    assert r.status_code == 302
    with client.application.app_context():
        at = db.session.get(Atendimento, at_id)
        assert at.status == "CONCLUIDO"
        assert at.data_saida is not None


def test_editar_veiculo_salva_mudancas(client):
    _login(client)
    with client.application.app_context():
        veiculo = Veiculo.query.first()
        cliente_id = Cliente.query.first().id
        v_id = veiculo.id
        placa = veiculo.placa
        assert veiculo_service.buscar_por_id(v_id).marca != "Marca Atualizada"
    r = client.post(
        "/veiculos/salvar",
        data={
            "id": str(v_id),
            "placa": placa,
            "marca": "Marca Atualizada",
            "modelo": "Modelo Editado",
            "ano": "2019",
            "cor": "Vermelho",
            "cliente.id": str(cliente_id),
        },
    )
    assert r.status_code == 302
    assert r.headers["Location"] == "/veiculos"
    with client.application.app_context():
        v = db.session.get(Veiculo, v_id)
        assert v.marca == "Marca Atualizada"
        assert v.modelo == "Modelo Editado"
        assert v.cor == "Vermelho"


def test_editar_despesa_salva_mudancas(client):
    _login(client)
    with client.application.app_context():
        despesa = Despesa.query.first()
        d_id = despesa.id
    r = client.post(
        "/despesas/salvar",
        data={
            "id": str(d_id),
            "descricao": "Despesa atualizada",
            "valorText": "99,90",
            "data": "2026-09-21",
            "categoria": "OUTROS",
        },
    )
    assert r.status_code == 302
    with client.application.app_context():
        d = db.session.get(Despesa, d_id)
        assert d.descricao == "Despesa atualizada"
        assert float(d.valor) == 99.90


def test_editar_orcamento_substitui_itens_e_recalcula(client):
    _login(client)
    with client.application.app_context():
        orc = Orcamento.query.first()
        o_id = orc.id
        at_id = orc.atendimento_id
    r = client.post(
        "/orcamentos/salvar",
        data={
            "id": str(o_id),
            "atendimentoId": str(at_id),
            "status": "APROVADO",
            "observacoes": "Editado no teste",
            "valorMaoDeObraText": "30,00",
            "itemDescricao": ["Serviço de teste"],
            "itemQuantidade": ["1"],
            "itemValorUnitario": ["50,00"],
        },
    )
    assert r.status_code == 302
    assert r.headers["Location"] == f"/atendimentos/{at_id}"
    with client.application.app_context():
        orc = db.session.get(Orcamento, o_id)
        assert orc.status == "APROVADO"
        assert orc.observacoes == "Editado no teste"
        assert len(orc.itens) == 1
        assert orc.itens[0].descricao == "Serviço de teste"
        assert float(orc.valor_total) == 80.00


def test_remover_veiculo_com_atendimento_bloqueado(client):
    _login(client)
    with client.application.app_context():
        veiculo = Veiculo.query.filter(Veiculo.atendimentos.any()).first()
        v_id = veiculo.id
    r = client.post(f"/veiculos/{v_id}/remover")
    assert r.status_code == 302
    assert r.headers["Location"] == "/veiculos"
    with client.application.app_context():
        assert db.session.get(Veiculo, v_id) is not None


def test_remover_veiculo_sem_atendimento_ok(client):
    _login(client)
    with client.application.app_context():
        cliente_id = Cliente.query.first().id
    r = client.post(
        "/veiculos/salvar",
        data={
            "placa": "REM-0001",
            "marca": "Remocao",
            "modelo": "Teste",
            "ano": "2020",
            "cor": "Branco",
            "cliente.id": str(cliente_id),
        },
    )
    assert r.status_code == 302
    with client.application.app_context():
        v = db.session.execute(db.select(Veiculo).where(Veiculo.placa == "REM-0001")).scalars().first()
        v_id = v.id
    r = client.post(f"/veiculos/{v_id}/remover")
    assert r.status_code == 302
    with client.application.app_context():
        assert db.session.get(Veiculo, v_id) is None


def test_relatorio_orcamentos_carrega(client):
    _login(client)
    r = client.get("/relatorios/orcamentos")
    assert r.status_code == 200
    assert "Relatório de Orçamentos" in r.get_data(as_text=True)


def test_relatorio_orcamentos_filtros(client):
    _login(client)
    r = client.get(
        "/relatorios/orcamentos?dataInicio=2020-01-01&dataFim=2030-12-31&status=PENDENTE"
    )
    assert r.status_code == 200
    assert "Relatório de Orçamentos" in r.get_data(as_text=True)


def test_pecas_removido_da_navegacao(client):
    _login(client)
    r = client.get("/")
    assert "Peças" not in r.get_data(as_text=True)
    assert "/pecas" not in r.get_data(as_text=True)


def test_criar_despesa(client):
    _login(client)
    r = client.post(
        "/despesas/salvar",
        data={
            "descricao": "Compra de teste",
            "valorText": "12,50",
            "data": "2026-09-21",
            "categoria": "PRODUTOS",
        },
    )
    assert r.status_code == 302
    assert r.headers["Location"] == "/despesas"
    with client.application.app_context():
        assert (
            db.session.execute(
                db.select(Despesa).where(Despesa.descricao == "Compra de teste")
            ).scalar_one_or_none()
            is not None
        )


def test_gerar_parcelas(client):
    _login(client)
    with client.application.app_context():
        orc = Orcamento.query.first()
        orc_id = orc.id
        atendimento_id = orc.atendimento_id
        total = float(orc.valor_total)
    r = client.post(
        f"/orcamentos/{orc_id}/parcelar",
        data={"quantidadeParcelas": "3"},
    )
    assert r.status_code == 302
    assert r.headers["Location"] == f"/atendimentos/{atendimento_id}/finalizar"
    with client.application.app_context():
        orc = db.session.get(Orcamento, orc_id)
        assert len(orc.parcelas) == 3
        assert all(p.status_pagamento == "PENDENTE" for p in orc.parcelas)
        soma = sum(float(p.valor) for p in orc.parcelas)
        assert abs(soma - total) < 0.01
        vencimentos = [p.vencimento for p in orc.parcelas]
        assert vencimentos[0] < vencimentos[1] < vencimentos[2]


def test_gerar_parcelas_quantidade_invalida(client):
    _login(client)
    with client.application.app_context():
        orc = Orcamento.query.first()
        orc_id = orc.id
    r = client.post(
        f"/orcamentos/{orc_id}/parcelar",
        data={"quantidadeParcelas": "1"},
    )
    assert r.status_code == 302
    with client.application.app_context():
        orc = db.session.get(Orcamento, orc_id)
        assert not orc.parcelas


def test_nao_parcelar_duas_vezes(client):
    _login(client)
    with client.application.app_context():
        orc = Orcamento.query.first()
        orc_id = orc.id
    client.post(f"/orcamentos/{orc_id}/parcelar", data={"quantidadeParcelas": "3"})
    r = client.post(f"/orcamentos/{orc_id}/parcelar", data={"quantidadeParcelas": "6"})
    assert r.status_code == 302
    with client.application.app_context():
        orc = db.session.get(Orcamento, orc_id)
        assert len(orc.parcelas) == 3
        assert orc.parcelas[0].total_parcelas == 3


def test_pagamento_parcela_parcial(client):
    _login(client)
    with client.application.app_context():
        orc = Orcamento.query.first()
        orc_id = orc.id
        atendimento_id = orc.atendimento_id
        valor_primeira = float(orc.valor_total / 3)
    client.post(f"/orcamentos/{orc_id}/parcelar", data={"quantidadeParcelas": "3"})
    with client.application.app_context():
        orc = db.session.get(Orcamento, orc_id)
        ids = [str(p.id) for p in orc.parcelas]
    r = client.post(
        f"/atendimentos/{atendimento_id}/pagamentos",
        data={
            "parcelaId": ids,
            "parcelaSituacao": ["PAGO", "PENDENTE", "PENDENTE"],
            "parcelaForma": ["DINHEIRO", "", ""],
            "parcelaValor": ["", "", ""],
            "parcelaData": ["", "", ""],
        },
    )
    assert r.status_code == 302
    with client.application.app_context():
        orc = db.session.get(Orcamento, orc_id)
        assert orc.status_pagamento == "PENDENTE"
        assert abs(float(orc.valor_pago) - round(valor_primeira, 2)) < 0.05
        primeira = min(orc.parcelas, key=lambda p: p.numero)
        assert primeira.status_pagamento == "PAGO"


def test_pagamento_parcelas_quitado(client):
    _login(client)
    with client.application.app_context():
        orc = Orcamento.query.first()
        orc_id = orc.id
        atendimento_id = orc.atendimento_id
        total = float(orc.valor_total)
    client.post(f"/orcamentos/{orc_id}/parcelar", data={"quantidadeParcelas": "2"})
    with client.application.app_context():
        orc = db.session.get(Orcamento, orc_id)
        ids = [str(p.id) for p in orc.parcelas]
    r = client.post(
        f"/atendimentos/{atendimento_id}/pagamentos",
        data={
            "parcelaId": ids,
            "parcelaSituacao": ["PAGO", "PAGO"],
            "parcelaForma": ["PIX", "PIX"],
            "parcelaValor": ["", ""],
            "parcelaData": ["", ""],
        },
    )
    assert r.status_code == 302
    with client.application.app_context():
        orc = db.session.get(Orcamento, orc_id)
        assert orc.status_pagamento == "PAGO"
        assert all(p.status_pagamento == "PAGO" for p in orc.parcelas)
        assert abs(float(orc.valor_pago) - total) < 0.01