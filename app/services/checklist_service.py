from datetime import datetime
from zoneinfo import ZoneInfo

from app.extensions import db
from app.models import Atendimento, ChecklistEntrada, FotoChecklist

from .file_storage_service import file_storage_service

BR_TZ = ZoneInfo("America/Sao_Paulo")


class ChecklistService:
    def listar_todos(self):
        return sorted(
            ChecklistEntrada.query.all(),
            key=lambda c: c.data_entrada,
            reverse=True,
        )

    def buscar(self, veiculo_id, data_inicio, data_fim, responsavel):
        resultados = []
        # Datas vêm da query string. Um filtro malformado não pode estourar 500
        # no `fromisoformat`: a tela tem que abrir e simplesmente ignorar o
        # filtro que não dá para interpretar.
        try:
            if data_inicio is not None and data_inicio.strip():
                ini = datetime.fromisoformat(f"{data_inicio}T00:00:00").replace(tzinfo=BR_TZ)
            else:
                ini = None
        except ValueError:
            ini = None
        try:
            if data_fim is not None and data_fim.strip():
                fim = datetime.fromisoformat(f"{data_fim}T23:59:59").replace(tzinfo=BR_TZ)
            else:
                fim = None
        except ValueError:
            fim = None

        for c in ChecklistEntrada.query.all():
            if veiculo_id is not None and veiculo_id.strip():
                if str(c.veiculo.id) != veiculo_id:
                    continue
            if ini is not None and c.data_entrada < ini:
                continue
            if fim is not None and c.data_entrada > fim:
                continue
            if responsavel is not None and responsavel.strip():
                if c.responsavel is None or responsavel.lower() not in c.responsavel.lower():
                    continue
            resultados.append(c)
        resultados.sort(key=lambda c: c.data_entrada, reverse=True)
        return resultados

    def buscar_por_id(self, id_):
        return db.session.get(ChecklistEntrada, id_)

    def _adicionar_fotos(self, checklist, fotos, descricoes):
        if not fotos:
            return
        indice = 0
        for foto in fotos:
            if foto is None or not foto.filename:
                indice += 1
                continue
            caminho = file_storage_service.salvar(foto, f"checklists/{checklist.id}")
            if caminho is not None:
                descricao = descricoes.get(str(indice)) if descricoes else None
                checklist.fotos.append(
                    FotoChecklist(
                        checklist_id=checklist.id,
                        caminho_arquivo=caminho,
                        descricao=descricao,
                    )
                )
            indice += 1

    def _criar_atendimento(self, checklist):
        atendimento = Atendimento(
            veiculo_id=checklist.veiculo_id,
            checklist_entrada_id=checklist.id,
            status="EM_ANDAMENTO",
            mecanico_responsavel=checklist.responsavel,
            observacoes=checklist.observacoes_gerais,
        )
        db.session.add(atendimento)

    def salvar(self, checklist, fotos=None, descricoes=None):
        if checklist.data_entrada is None:
            checklist.data_entrada = datetime.now(BR_TZ)
        if checklist.id is not None:
            existente = self.buscar_por_id(checklist.id)
            if existente is not None:
                existente.veiculo_id = checklist.veiculo_id
                existente.data_entrada = checklist.data_entrada
                existente.quilometragem = checklist.quilometragem
                existente.nivel_combustivel = checklist.nivel_combustivel
                existente.condicoes_lataria = checklist.condicoes_lataria
                existente.observacoes_gerais = checklist.observacoes_gerais
                existente.responsavel = checklist.responsavel
                self._adicionar_fotos(existente, fotos, descricoes)
                db.session.commit()
                return existente
        db.session.add(checklist)
        db.session.flush()
        self._adicionar_fotos(checklist, fotos, descricoes)
        db.session.commit()
        self._criar_atendimento(checklist)
        db.session.commit()
        return checklist

    def remover_foto(self, foto_id):
        foto = db.session.get(FotoChecklist, foto_id)
        if foto is None:
            return
        checklist = foto.checklist
        file_storage_service.remover(foto.caminho_arquivo)
        db.session.delete(foto)
        db.session.commit()

    def salvar_dados_basicos(self, checklist):
        db.session.add(checklist)
        db.session.commit()


checklist_service = ChecklistService()