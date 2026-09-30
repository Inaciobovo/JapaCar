import re

from app.extensions import db
from app.models import Cliente, Veiculo


class VeiculoService:
    def listar_todos(self):
        return sorted(Veiculo.query.all(), key=lambda v: (v.placa or "").lower())

    def buscar(self, termo):
        if termo is None or not termo.strip():
            return self.listar_todos()
        t = termo.strip()
        por_placa = (
            Veiculo.query.filter(Veiculo.placa.ilike(f"%{t}%"))
            .order_by(Veiculo.placa.asc())
            .all()
        )
        por_modelo = (
            Veiculo.query.filter(Veiculo.modelo.ilike(f"%{t}%"))
            .order_by(Veiculo.modelo.asc())
            .all()
        )
        vistos = {v.id for v in por_placa}
        resultado = list(por_placa)
        for v in por_modelo:
            if v.id not in vistos:
                resultado.append(v)
        return resultado

    def listar_por_cliente(self, cliente_id):
        return (
            Veiculo.query.filter_by(cliente_id=cliente_id)
            .order_by(Veiculo.placa.asc())
            .all()
        )

    def buscar_por_id(self, id_):
        return db.session.get(Veiculo, id_)

    def placa_ja_cadastrada(self, placa, id_ignorar=None):
        if placa is None or not placa.strip():
            return False
        p = re.sub(r"\s", "", placa).upper()
        for v in Veiculo.query.all():
            if (
                re.sub(r"\s", "", v.placa).upper() == p
                and v.id != id_ignorar
            ):
                return True
        return False

    def salvar(self, veiculo):
        if veiculo.placa is not None:
            veiculo.placa = veiculo.placa.strip().upper()
        cliente = None
        if veiculo.cliente is not None and veiculo.cliente.id is not None:
            cliente = db.session.get(Cliente, veiculo.cliente.id)
        if veiculo.id is not None:
            existente = self.buscar_por_id(veiculo.id)
            if existente is not None:
                existente.placa = veiculo.placa
                existente.modelo = veiculo.modelo
                existente.marca = veiculo.marca
                existente.ano = veiculo.ano
                existente.cor = veiculo.cor
                if cliente is not None:
                    existente.cliente = cliente
                db.session.commit()
                return existente
        veiculo.cliente = cliente
        db.session.add(veiculo)
        db.session.commit()
        return veiculo

    def remover(self, id_):
        veiculo = self.buscar_por_id(id_)
        if veiculo is None:
            return False
        from app.models import Atendimento

        if Atendimento.query.filter_by(veiculo_id=id_).count() > 0:
            return False
        db.session.delete(veiculo)
        db.session.commit()
        return True


veiculo_service = VeiculoService()