from datetime import date

from app.extensions import db
from app.models import Despesa


def _data_iso(valor):
    if not valor or not str(valor).strip():
        return None
    try:
        return date.fromisoformat(str(valor).strip())
    except ValueError:
        return None


class DespesaService:
    def listar_todas(self):
        return Despesa.query.order_by(Despesa.data.desc()).all()

    def buscar(self, data_inicio, data_fim, categoria):
        # Filtros vêm da query string; data ilegível é ignorada em vez de
        # derrubar a tela com ValueError.
        inicio = _data_iso(data_inicio)
        fim = _data_iso(data_fim)

        if inicio is not None and fim is not None and (categoria is None or not categoria.strip()):
            return (
                Despesa.query.filter(Despesa.data.between(inicio, fim))
                .order_by(Despesa.data.desc())
                .all()
            )
        if inicio is not None and fim is not None and categoria and categoria.strip():
            return (
                Despesa.query.filter(
                    Despesa.data.between(inicio, fim),
                    Despesa.categoria == categoria,
                )
                .order_by(Despesa.data.desc())
                .all()
            )
        if categoria and categoria.strip():
            return (
                Despesa.query.filter_by(categoria=categoria)
                .order_by(Despesa.data.desc())
                .all()
            )
        return self.listar_todas()

    def buscar_por_id(self, id_):
        return db.session.get(Despesa, id_)

    def salvar(self, despesa):
        if despesa.id is not None:
            existente = self.buscar_por_id(despesa.id)
            if existente is not None:
                existente.descricao = despesa.descricao
                existente.categoria = despesa.categoria
                existente.observacoes = despesa.observacoes
                existente.data = despesa.data
                existente.valor = despesa.valor
                db.session.commit()
                return existente
        db.session.add(despesa)
        db.session.commit()
        return despesa

    def remover(self, id_):
        despesa = self.buscar_por_id(id_)
        if despesa is not None:
            db.session.delete(despesa)
            db.session.commit()


despesa_service = DespesaService()