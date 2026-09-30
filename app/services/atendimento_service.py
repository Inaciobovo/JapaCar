from datetime import datetime
from zoneinfo import ZoneInfo

from app.extensions import db
from app.models import Atendimento

BR_TZ = ZoneInfo("America/Sao_Paulo")


class AtendimentoService:
    def listar_todos(self):
        return Atendimento.query.order_by(Atendimento.data_entrada.desc()).all()

    def listar_por_status(self, status):
        return (
            Atendimento.query.filter_by(status=status)
            .order_by(Atendimento.data_entrada.desc())
            .all()
        )

    def buscar_por_id(self, id_):
        return db.session.get(Atendimento, id_)

    def salvar(self, atendimento):
        if atendimento.status is None:
            atendimento.status = "EM_ANDAMENTO"
        db.session.add(atendimento)
        db.session.commit()
        return atendimento

    def inativar(self, id_):
        atendimento = self.buscar_por_id(id_)
        if atendimento is None:
            return
        atendimento.status = "CANCELADO"
        db.session.commit()

    def finalizar(self, id_):
        atendimento = self.buscar_por_id(id_)
        if atendimento is None or atendimento.status != "EM_ANDAMENTO":
            return
        atendimento.status = "CONCLUIDO"
        atendimento.data_saida = datetime.now(BR_TZ)
        for orcamento in atendimento.orcamentos:
            if orcamento.status in ("PENDENTE", "APROVADO", "REJEITADO"):
                orcamento.status = "CONCLUIDO"
        db.session.commit()


atendimento_service = AtendimentoService()