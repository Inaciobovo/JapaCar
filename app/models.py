from datetime import date, datetime, time
from decimal import Decimal
from zoneinfo import ZoneInfo

from flask_login import UserMixin
from sqlalchemy import BigInteger, TypeDecorator

from app.extensions import db

BR_TZ = ZoneInfo("America/Sao_Paulo")


def now_br() -> datetime:
    return datetime.now(BR_TZ)


def _dec(valor):
    if valor is None:
        return Decimal("0")
    if isinstance(valor, Decimal):
        return valor
    return Decimal(valor)


class EpochMsDateTime(TypeDecorator):
    """Coluna INTEGER epoch-milliseconds (instante local em America/Sao_Paulo).

    Armazena datetimes como inteiros (milissegundos desde a época) no SQLite,
    mantendo compatibilidade com dados já persistidos em formato numérico.
    """

    impl = BigInteger
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        dt = value
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=BR_TZ)
        return int(dt.timestamp() * 1000)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return datetime.fromtimestamp(value / 1000, BR_TZ)


class EpochMsDate(TypeDecorator):
    """Coluna INTEGER epoch-milliseconds de uma data (meia-noite local).

    Armazena datas como inteiros (milissegundos desde a época, à 00:00 local)
    para manter compatibilidade com dados já persistidos em formato numérico.
    """

    impl = BigInteger
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        d = value
        if isinstance(d, datetime):
            d = d.date()
        return int(datetime.combine(d, time.min, tzinfo=BR_TZ).timestamp() * 1000)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return datetime.fromtimestamp(value / 1000, BR_TZ).date()


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    login = db.Column(db.String(255), nullable=False, unique=True)
    senha = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(255), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    @property
    def username(self):
        return self.login

    @property
    def perfil_descricao(self):
        return PERFIL_DESCRICOES.get(self.perfil, self.perfil)


class Cliente(db.Model):
    __tablename__ = "cliente"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(255), unique=True)
    telefone = db.Column(db.String(255))
    email = db.Column(db.String(255))
    endereco = db.Column(db.String(255))
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    data_criacao = db.Column(EpochMsDateTime, nullable=False, default=now_br)

    veiculos = db.relationship(
        "Veiculo", back_populates="cliente", cascade="all, delete-orphan"
    )


class Veiculo(db.Model):
    __tablename__ = "veiculo"

    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(255), nullable=False)
    modelo = db.Column(db.String(255), nullable=False)
    marca = db.Column(db.String(255), nullable=False)
    ano = db.Column(db.Integer)
    cor = db.Column(db.String(255))
    cliente_id = db.Column(
        db.Integer, db.ForeignKey("cliente.id"), nullable=False
    )

    cliente = db.relationship("Cliente", back_populates="veiculos", lazy="select")
    atendimentos = db.relationship("Atendimento", back_populates="veiculo", lazy="select")


class ChecklistEntrada(db.Model):
    __tablename__ = "checklist_entrada"

    id = db.Column(db.Integer, primary_key=True)
    veiculo_id = db.Column(
        db.Integer, db.ForeignKey("veiculo.id"), nullable=False
    )
    data_entrada = db.Column(EpochMsDateTime, nullable=False, default=now_br)
    quilometragem = db.Column(db.Integer)
    nivel_combustivel = db.Column(db.String(255))
    condicoes_lataria = db.Column(db.String(2000))
    observacoes_gerais = db.Column(db.String(2000))
    responsavel = db.Column(db.String(255))

    veiculo = db.relationship("Veiculo", lazy="select")
    fotos = db.relationship(
        "FotoChecklist",
        back_populates="checklist",
        cascade="all, delete-orphan",
        lazy="select",
    )


class FotoChecklist(db.Model):
    __tablename__ = "foto_checklist"

    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(
        db.Integer, db.ForeignKey("checklist_entrada.id"), nullable=False
    )
    caminho_arquivo = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.String(255))

    checklist = db.relationship(
        "ChecklistEntrada", back_populates="fotos", lazy="select"
    )


class Atendimento(db.Model):
    __tablename__ = "atendimento"

    id = db.Column(db.Integer, primary_key=True)
    veiculo_id = db.Column(db.Integer, db.ForeignKey("veiculo.id"), nullable=False)
    checklist_entrada_id = db.Column(
        db.Integer, db.ForeignKey("checklist_entrada.id")
    )
    data_entrada = db.Column(EpochMsDateTime, nullable=False, default=now_br)
    data_saida = db.Column(EpochMsDateTime)
    status = db.Column(db.String(255), nullable=False, default="EM_ANDAMENTO")
    mecanico_responsavel = db.Column(db.String(255))
    conferente = db.Column(db.String(255))
    observacoes = db.Column(db.String(255))

    veiculo = db.relationship("Veiculo", back_populates="atendimentos", lazy="select")
    checklist_entrada = db.relationship("ChecklistEntrada", lazy="select")
    orcamentos = db.relationship(
        "Orcamento",
        back_populates="atendimento",
        order_by="Orcamento.data_criacao.desc()",
        lazy="select",
    )

    @property
    def status_descricao(self):
        return STATUS_ATENDIMENTO_DESCRICOES.get(self.status, self.status)


class Orcamento(db.Model):
    __tablename__ = "orcamento"

    id = db.Column(db.Integer, primary_key=True)
    atendimento_id = db.Column(
        db.Integer, db.ForeignKey("atendimento.id"), nullable=False
    )
    data_criacao = db.Column(EpochMsDateTime, nullable=False, default=now_br)
    valor_mao_de_obra = db.Column(db.Numeric(10, 2), default=0)
    valor_pecas = db.Column(db.Numeric(10, 2), default=0)
    valor_total = db.Column(db.Numeric(10, 2), default=0)
    status = db.Column(db.String(255), nullable=False, default="PENDENTE")
    status_pagamento = db.Column(db.String(255), nullable=False, default="PENDENTE")
    forma_pagamento = db.Column(db.String(255))
    data_pagamento = db.Column(EpochMsDate)
    valor_pago = db.Column(db.Numeric(10, 2), default=0)
    observacoes = db.Column(db.String(255))

    atendimento = db.relationship(
        "Atendimento", back_populates="orcamentos", lazy="select"
    )
    itens = db.relationship(
        "ItemServico",
        back_populates="orcamento",
        cascade="all, delete-orphan",
        order_by="ItemServico.id",
        lazy="select",
    )
    parcelas = db.relationship(
        "Parcela",
        back_populates="orcamento",
        cascade="all, delete-orphan",
        order_by="Parcela.numero",
        lazy="select",
    )

    def recalcular_totais(self):
        total_pecas = Decimal(0)
        for item in self.itens:
            total_pecas += item.subtotal
        self.valor_pecas = total_pecas
        self.valor_total = total_pecas + _dec(self.valor_mao_de_obra)

    @property
    def status_descricao(self):
        return STATUS_ORCAMENTO_DESCRICOES.get(self.status, self.status)

    @property
    def status_pagamento_descricao(self):
        return STATUS_PAGAMENTO_DESCRICOES.get(
            self.status_pagamento or "PENDENTE", self.status_pagamento
        )

    @property
    def forma_pagamento_descricao(self):
        return FORMA_PAGAMENTO_DESCRICOES.get(self.forma_pagamento, self.forma_pagamento)

    @property
    def valor_pago_real(self):
        return _dec(self.valor_pago)

    @property
    def parcelado(self):
        return bool(self.parcelas)

    @property
    def valor_restante(self):
        total = _dec(self.valor_total)
        pago = _dec(self.valor_pago)
        return max(total - pago, Decimal("0"))


class Parcela(db.Model):
    __tablename__ = "parcela"

    id = db.Column(db.Integer, primary_key=True)
    orcamento_id = db.Column(
        db.Integer, db.ForeignKey("orcamento.id"), nullable=False
    )
    numero = db.Column(db.Integer, nullable=False)
    total_parcelas = db.Column(db.Integer, nullable=False, default=1)
    valor = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    vencimento = db.Column(EpochMsDate, nullable=False)
    status_pagamento = db.Column(db.String(255), nullable=False, default="PENDENTE")
    forma_pagamento = db.Column(db.String(255))
    valor_pago = db.Column(db.Numeric(10, 2), default=0)
    data_pagamento = db.Column(EpochMsDate)
    observacoes = db.Column(db.String(255))

    orcamento = db.relationship("Orcamento", back_populates="parcelas", lazy="select")

    @property
    def status_pagamento_descricao(self):
        return STATUS_PAGAMENTO_DESCRICOES.get(
            self.status_pagamento or "PENDENTE", self.status_pagamento
        )

    @property
    def rotulo(self):
        return f"{self.numero}/{self.total_parcelas or self.numero}"


class ItemServico(db.Model):
    __tablename__ = "item_servico"

    id = db.Column(db.Integer, primary_key=True)
    orcamento_id = db.Column(
        db.Integer, db.ForeignKey("orcamento.id"), nullable=False
    )
    descricao = db.Column(db.String(500), nullable=False)
    peca_id = db.Column(db.Integer, db.ForeignKey("peca.id"))
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    valor_unitario = db.Column(db.Numeric(10, 2))

    orcamento = db.relationship("Orcamento", back_populates="itens", lazy="select")
    peca = db.relationship("Peca", lazy="select")

    @property
    def subtotal(self):
        unit = _dec(self.valor_unitario)
        qtd = self.quantidade if self.quantidade is not None else 1
        return unit * qtd


class Peca(db.Model):
    __tablename__ = "peca"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(255), unique=True)
    nome = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.String(500))
    preco_compra = db.Column(db.Numeric(10, 2))
    preco_venda = db.Column(db.Numeric(10, 2))
    estoque = db.Column(db.Integer, nullable=False, default=0)


class Despesa(db.Model):
    __tablename__ = "despesa"

    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(500), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data = db.Column(EpochMsDate, nullable=False)
    categoria = db.Column(db.String(255), nullable=False)
    observacoes = db.Column(db.String(255))
    data_criacao = db.Column(EpochMsDateTime, nullable=False, default=now_br)

    @property
    def categoria_descricao(self):
        return CATEGORIA_DESCRICOES.get(self.categoria, self.categoria)


STATUS_ATENDIMENTO_DESCRICOES = {
    "EM_ANDAMENTO": "Em andamento",
    "CONCLUIDO": "Concluído",
    "CANCELADO": "Cancelado",
}

STATUS_ORCAMENTO_DESCRICOES = {
    "PENDENTE": "Pendente",
    "APROVADO": "Aprovado",
    "REJEITADO": "Rejeitado",
    "CONCLUIDO": "Concluído",
    "INATIVO": "Inativo",
}

STATUS_PAGAMENTO_DESCRICOES = {
    "PENDENTE": "Pendente",
    "PAGO": "Pago",
}

FORMA_PAGAMENTO_DESCRICOES = {
    "DINHEIRO": "Dinheiro",
    "PIX": "Pix",
    "CARTAO_DEBITO": "Cartão de débito",
    "CARTAO_CREDITO": "Cartão de crédito",
    "TRANSFERENCIA": "Transferência",
    "BOLETO": "Boleto",
    "OUTROS": "Outros",
}

NIVEL_COMBUSTIVEL_DESCRICOES = {
    "CHEIO": "Tanque cheio",
    "TRES_QUARTOS": "3/4 - Três quartos",
    "METADE": "1/2 - Metade",
    "UM_QUARTO": "1/4 - Um quarto",
    "RESERVA": "Reserva",
    "VAZIO": "Vazio",
}

CATEGORIA_DESCRICOES = {
    "ALUGUEL": "Aluguel",
    "FUNCIONARIOS": "Funcionários",
    "MATERIAIS": "Materiais",
    "PRODUTOS": "Produtos",
    "SERVICOS": "Serviços",
    "ENERGIA": "Energia",
    "AGUA": "Água",
    "TELEFONE": "Telefone",
    "IMPOSTOS": "Impostos",
    "OUTROS": "Outros",
}

PERFIL_DESCRICOES = {
    "ADMIN": "Administrador",
    "MECANICO": "Mecânico",
    "ATENDENTE": "Atendente",
}