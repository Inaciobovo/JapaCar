import calendar
from datetime import date

from app.extensions import db
from app.models import Atendimento, Cliente, Despesa, Orcamento

MESES_PT_BR = [
    "jan.",
    "fev.",
    "mar.",
    "abr.",
    "mai.",
    "jun.",
    "jul.",
    "ago.",
    "set.",
    "out.",
    "nov.",
    "dez.",
]


class DashboardService:
    def get_dashboard(self):
        hoje = date.today()
        inicio_mes = hoje.replace(day=1)
        fim_mes = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1])

        receitas = self._receitas_no_periodo(inicio_mes, fim_mes)
        despesas = self._despesas_no_periodo(inicio_mes, fim_mes)

        atendimentos_em_andamento = Atendimento.query.filter_by(status="EM_ANDAMENTO").count()
        atendimentos_concluidos = Atendimento.query.filter_by(status="CONCLUIDO").count()
        orcamentos_pendentes = Orcamento.query.filter_by(status="PENDENTE").count()
        clientes_ativos = Cliente.query.filter_by(ativo=True).count()

        por_categoria = (
            db.session.query(Despesa.categoria, db.func.sum(Despesa.valor))
            .filter(Despesa.data.between(inicio_mes, fim_mes))
            .group_by(Despesa.categoria)
            .order_by(db.func.sum(Despesa.valor).desc())
            .all()
        )
        top_despesas = [
            {"categoria": _categoria_descricao(cat), "total": total or 0}
            for cat, total in por_categoria
        ]

        resumo = []
        ym = self._ym(hoje).minus(5)
        for i in range(6):
            periodo = ym.plus(i)
            ini = date(periodo.year, periodo.month, 1)
            fim = date(
                periodo.year,
                periodo.month,
                calendar.monthrange(periodo.year, periodo.month)[1],
            )
            rec = self._receitas_no_periodo(ini, fim)
            desp = self._despesas_no_periodo(ini, fim)
            resumo.append(
                {
                    "mes": MESES_PT_BR[periodo.month - 1],
                    "receitas": rec,
                    "despesas": desp,
                }
            )

        return {
            "receitasMes": receitas,
            "despesasMes": despesas,
            "saldoMes": receitas - despesas,
            "atendimentosEmAndamento": atendimentos_em_andamento,
            "atendimentosConcluidos": atendimentos_concluidos,
            "orcamentosPendentes": orcamentos_pendentes,
            "clientesAtivos": clientes_ativos,
            "topDespesasPorCategoria": top_despesas,
            "resumoMensal": resumo,
        }

    @staticmethod
    def _ym(hoje):
        class _Ym:
            def __init__(self, year, month):
                self.year = year
                self.month = month

            def minus(self, months):
                total = self.year * 12 + (self.month - 1) - months
                return _Ym(total // 12, total % 12 + 1)

            def plus(self, months):
                total = self.year * 12 + (self.month - 1) + months
                return _Ym(total // 12, total % 12 + 1)

            def __iter__(self):
                return iter((self.year, self.month))

        return _Ym(hoje.year, hoje.month)

    def _receitas_no_periodo(self, inicio, fim):
        return (
            db.session.query(db.func.coalesce(db.func.sum(Orcamento.valor_pago), 0))
            .filter(
                Orcamento.status_pagamento == "PAGO",
                Orcamento.data_pagamento.isnot(None),
                Orcamento.data_pagamento.between(inicio, fim),
            )
            .scalar()
        ) or 0

    def _despesas_no_periodo(self, inicio, fim):
        return (
            db.session.query(db.func.coalesce(db.func.sum(Despesa.valor), 0))
            .filter(Despesa.data.between(inicio, fim))
            .scalar()
        ) or 0


def _categoria_descricao(categoria):
    from app.models import CATEGORIA_DESCRICOES

    return CATEGORIA_DESCRICOES.get(categoria, categoria)


dashboard_service = DashboardService()