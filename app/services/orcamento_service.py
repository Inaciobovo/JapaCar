import calendar
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

from app.extensions import db
from app.models import Orcamento, Parcela, _dec

from app.utils import parse_data, parse_valor, valor_valido

BR_TZ = ZoneInfo("America/Sao_Paulo")


class OrcamentoService:
    def listar_todos(self):
        return Orcamento.query.order_by(Orcamento.data_criacao.desc()).all()

    def listar_por_status(self, status):
        return (
            Orcamento.query.filter_by(status=status)
            .order_by(Orcamento.data_criacao.desc())
            .all()
        )

    def buscar_por_id(self, id_):
        return db.session.get(Orcamento, id_)

    def listar_por_atendimento(self, atendimento_id):
        return (
            Orcamento.query.filter_by(atendimento_id=atendimento_id)
            .order_by(Orcamento.data_criacao.desc())
            .all()
        )

    def salvar(self, orcamento):
        orcamento.itens = [
            item
            for item in orcamento.itens
            if item.descricao is not None and item.descricao.strip()
        ]
        if orcamento.status is None:
            orcamento.status = "PENDENTE"
        if orcamento.id is not None:
            existente = self.buscar_por_id(orcamento.id)
            if existente is not None:
                existente.atendimento = orcamento.atendimento
                existente.status = orcamento.status
                existente.observacoes = orcamento.observacoes
                existente.valor_mao_de_obra = orcamento.valor_mao_de_obra
                for item in list(existente.itens):
                    db.session.delete(item)
                db.session.flush()
                novos = []
                for item in orcamento.itens:
                    item.orcamento = existente
                    db.session.add(item)
                    novos.append(item)
                existente.itens = novos
                existente.recalcular_totais()
                db.session.commit()
                return existente
        orcamento.recalcular_totais()
        if orcamento.data_criacao is None:
            orcamento.data_criacao = datetime.now(BR_TZ)
        db.session.add(orcamento)
        db.session.flush()
        for item in orcamento.itens:
            item.orcamento_id = orcamento.id
            db.session.add(item)
        db.session.commit()
        return orcamento

    def inativar(self, id_):
        orcamento = self.buscar_por_id(id_)
        if orcamento is None:
            return
        orcamento.status = "INATIVO"
        db.session.commit()

    def aplicar_pagamentos(self, ids, situacoes, formas, valores, datas):
        if not ids:
            return
        for i, orc_id in enumerate(ids):
            if orc_id is None:
                continue
            orcamento = self.buscar_por_id(orc_id)
            if orcamento is None:
                continue
            # Orçamento parcelado se paga por parcela; aceitar um pagamento no
            # nível do orçamento aqui sobrescreveria o resultado da
            # sincronização das parcelas e permitiria contar o dinheiro duas
            # vezes. O template já separa os dois fluxos; esta guarda garante o
            # mesmo no servidor.
            if orcamento.parcelas:
                continue
            situacao = situacoes[i] if situacoes and i < len(situacoes) else None
            if situacao and situacao.upper() == "PAGO":
                orcamento.status_pagamento = "PAGO"
                forma = (
                    formas[i] if formas and i < len(formas) and formas[i] else None
                )
                orcamento.forma_pagamento = forma if forma and forma in FORMAS_VALIDAS else None
                total = _dec(orcamento.valor_total)
                valor = parse_valor(valores[i]) if valores and i < len(valores) else None
                # Valor fora de (0, total] corromperia o saldo e a receita do
                # dashboard: cai para o total devido.
                if not valor_valido(valor, minimo=Decimal("0.01"), maximo=total):
                    valor = total
                orcamento.valor_pago = valor
                orcamento.data_pagamento = (
                    parse_data(datas[i]) if datas and i < len(datas) else date.today()
                )
            else:
                orcamento.status_pagamento = "PENDENTE"
                orcamento.forma_pagamento = None
                orcamento.valor_pago = 0
                orcamento.data_pagamento = None
            db.session.commit()

    def gerar_parcelas(self, orcamento_id, quantidade):
        orcamento = self.buscar_por_id(orcamento_id)
        if orcamento is None:
            return None, "Orçamento não encontrado."
        if orcamento.valor_total is None or _dec(orcamento.valor_total) <= 0:
            return None, "Orçamento sem valor total válido para parcelar."
        try:
            quantidade = int(quantidade)
        except (TypeError, ValueError):
            return None, "Informe a quantidade de parcelas."
        if quantidade < 2:
            return None, "A quantidade de parcelas deve ser maior ou igual a 2."
        if quantidade > MAX_PARCELAS:
            return None, f"O número máximo de parcelas é {MAX_PARCELAS}."
        if orcamento.parcelas:
            return None, "Este orçamento já possui um plano de parcelas gerado."

        total = _dec(orcamento.valor_total)
        base = (total / Decimal(quantidade)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        hoje = date.today()
        somado = Decimal("0")
        nova_parcelas = []
        for i in range(1, quantidade + 1):
            if i == quantidade:
                valor = total - somado
            else:
                valor = base
                somado += valor
            nova_parcelas.append(
                Parcela(
                    numero=i,
                    total_parcelas=quantidade,
                    valor=valor,
                    vencimento=_adicionar_meses(hoje, i - 1),
                    status_pagamento="PENDENTE",
                )
            )
        orcamento.parcelas = nova_parcelas
        orcamento.status_pagamento = "PENDENTE"
        orcamento.data_pagamento = None
        db.session.commit()
        return orcamento, None

    def aplicar_pagamentos_parcelas(self, ids, situacoes, formas, valores, datas):
        if not ids:
            return
        for i, parcela_id in enumerate(ids):
            if parcela_id is None:
                continue
            parcela = db.session.get(Parcela, parcela_id)
            if parcela is None:
                continue
            situacao = situacoes[i] if situacoes and i < len(situacoes) else None
            if situacao and situacao.upper() == "PAGO":
                parcela.status_pagamento = "PAGO"
                forma = (
                    formas[i] if formas and i < len(formas) and formas[i] else None
                )
                parcela.forma_pagamento = (
                    forma if forma and forma in FORMAS_VALIDAS else None
                )
                devido = _dec(parcela.valor)
                valor = parse_valor(valores[i]) if valores and i < len(valores) else None
                # Mesma regra do pagamento à vista: valor fora de (0, devido]
                # cai para o valor da parcela, para não inflar o recebido.
                if not valor_valido(valor, minimo=Decimal("0.01"), maximo=devido):
                    valor = devido
                parcela.valor_pago = valor
                parcela.data_pagamento = (
                    parse_data(datas[i]) if datas and i < len(datas) else date.today()
                )
            else:
                parcela.status_pagamento = "PENDENTE"
                parcela.forma_pagamento = None
                parcela.valor_pago = 0
                parcela.data_pagamento = None
            self._sincronizar_orcamento(parcela.orcamento)
        db.session.commit()

    @staticmethod
    def _sincronizar_orcamento(orcamento):
        if orcamento is None or not orcamento.parcelas:
            return
        total_pago = sum(
            (_dec(p.valor_pago) for p in orcamento.parcelas if p.status_pagamento == "PAGO"),
            Decimal("0"),
        )
        orcamento.valor_pago = total_pago
        todas_pagas = all(p.status_pagamento == "PAGO" for p in orcamento.parcelas)
        if todas_pagas:
            orcamento.status_pagamento = "PAGO"
            orcamento.data_pagamento = max(
                (p.data_pagamento for p in orcamento.parcelas if p.data_pagamento),
                default=date.today(),
            )
        else:
            orcamento.status_pagamento = "PENDENTE"
            orcamento.data_pagamento = None


def _adicionar_meses(data, meses):
    mes_total = data.month - 1 + meses
    ano = data.year + mes_total // 12
    mes = mes_total % 12 + 1
    dia = min(data.day, calendar.monthrange(ano, mes)[1])
    return date(ano, mes, dia)


FORMAS_VALIDAS = {
    "DINHEIRO",
    "PIX",
    "CARTAO_DEBITO",
    "CARTAO_CREDITO",
    "TRANSFERENCIA",
    "BOLETO",
    "OUTROS",
}

# Teto do parcelamento. O template e o README falam de 2 a 12x; sem o limite no
# servidor, um POST direto podia gerar milhares de parcelas de centavos.
MAX_PARCELAS = 12


orcamento_service = OrcamentoService()