import re

from app.extensions import db
from app.models import Cliente


class ClienteService:
    def listar_ativos(self):
        return Cliente.query.filter_by(ativo=True).order_by(Cliente.nome.asc()).all()

    def listar_todos(self):
        return sorted(Cliente.query.all(), key=lambda c: c.nome.lower())

    def buscar(self, termo):
        if termo is None or not termo.strip():
            return self.listar_todos()
        t = termo.strip()
        por_nome = (
            Cliente.query.filter(Cliente.nome.ilike(f"%{t}%"))
            .order_by(Cliente.nome.asc())
            .all()
        )
        digitos = re.sub(r"\D", "", t)
        por_cpf = (
            Cliente.query.filter(Cliente.cpf.ilike(f"%{digitos}%"))
            .order_by(Cliente.nome.asc())
            .all()
        )
        vistos = {c.id for c in por_nome}
        resultado = list(por_nome)
        for c in por_cpf:
            if c.id not in vistos:
                resultado.append(c)
        return resultado

    def buscar_por_id(self, id_):
        return db.session.get(Cliente, id_)

    def cpf_ja_cadastrado(self, cpf, id_ignorar=None):
        if not cpf or not cpf.strip():
            return False
        somente_digitos = re.sub(r"\D", "", cpf)
        for c in Cliente.query.all():
            if (
                c.cpf is not None
                and re.sub(r"\D", "", c.cpf) == somente_digitos
                and c.id != id_ignorar
            ):
                return True
        return False

    def salvar(self, cliente):
        existente = self.buscar_por_id(cliente.id) if cliente.id is not None else None
        if existente is not None:
            existente.nome = cliente.nome
            existente.cpf = cliente.cpf if cliente.cpf is not None else None
            existente.telefone = cliente.telefone
            existente.email = cliente.email
            existente.endereco = cliente.endereco
            db.session.add(existente)
            db.session.commit()
            return existente
        db.session.add(cliente)
        db.session.commit()
        return cliente

    def inativar(self, id_):
        cliente = self.buscar_por_id(id_)
        if cliente is not None:
            cliente.ativo = False
            db.session.commit()


cliente_service = ClienteService()