from datetime import date
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.utils import format_brl

MARGEM = 36
LARGURA_A4 = A4[0]
LARGURA_UTIL = LARGURA_A4 - 2 * MARGEM

COR_TITULO = colors.HexColor("#1A1A2E")
COR_CABECALHO_TABELA = colors.HexColor("#1A1A2E")
COR_LINHA_ALTERNADA = colors.HexColor("#F3F4FA")
COR_DESTAQUE = colors.HexColor("#E7E8F0")
COR_CINZA = colors.Color(0.5, 0.5, 0.5)
COR_CINZA_ESCURO = colors.Color(0.3, 0.3, 0.3)

TAM_LABEL = 9
TAM_VALOR = 10


def _style(name, **kwargs):
    defaults = {
        "fontName": "Helvetica",
        "fontSize": TAM_VALOR,
        "leading": TAM_VALOR + 2,
        "textColor": colors.black,
        "alignment": TA_LEFT,
    }
    defaults.update(kwargs)
    return ParagraphStyle(name, **defaults)


def _moeda(valor):
    if valor is None:
        valor = Decimal("0")
    return f"R$ {format_brl(valor)}"


def _valor(texto):
    if texto is None or not str(texto).strip():
        return "—"
    return str(texto)


def gerar_pdf(orcamento) -> bytes:
    from io import BytesIO

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGEM,
        rightMargin=MARGEM,
        topMargin=MARGEM,
        bottomMargin=MARGEM,
        title=f"Orçamento Nº {orcamento.id if orcamento.id is not None else '-'}",
        author="JAPACAR",
    )

    elementos = []
    _cabecalho(elementos, orcamento)
    _dados_cliente(elementos, orcamento)
    _dados_veiculo(elementos, orcamento)
    _dados_servico(elementos, orcamento)
    _tabela_itens(elementos, orcamento)
    _totais(elementos, orcamento)
    _plano_parcelas(elementos, orcamento)
    _observacoes(elementos, orcamento)
    _rodape(elementos)

    doc.build(elementos)
    return buffer.getvalue()


def _cabecalho(elementos, orcamento):
    titulo = Paragraph(
        "JAPACAR",
        _style("titulo", fontName="Helvetica-Bold", fontSize=22,
               textColor=COR_TITULO, alignment=TA_CENTER),
    )
    sub = Paragraph(
        "Sistema de gestão para oficina mecânica",
        _style("sub", fontSize=9, textColor=COR_CINZA, alignment=TA_CENTER),
    )
    orc = Paragraph(
        f"ORÇAMENTO Nº {orcamento.id if orcamento.id is not None else '-'}",
        _style("orc", fontName="Helvetica-Bold", fontSize=16,
               textColor=COR_TITULO, alignment=TA_LEFT),
    )
    status = orcamento.status_descricao if orcamento.status else "-"
    data_criacao = orcamento.data_criacao
    emitido = data_criacao.strftime("%d/%m/%Y %H:%M") if data_criacao else "-"
    info = Paragraph(
        f"Emitido em: {emitido}    \u2022    Status: {status}",
        _style("info", fontSize=10),
    )
    pago = orcamento.status_pagamento == "PAGO"
    if pago:
        forma = orcamento.forma_pagamento
        pag = f"Pago ({orcamento.forma_pagamento_descricao})" if forma else "Pago"
    else:
        pag = "Pendente"
    pag_info = Paragraph(
        f"Situação do pagamento: {pag}", _style("pag", fontSize=10)
    )

    elementos.append(titulo)
    elementos.append(sub)
    elementos.append(Spacer(1, 14))
    elementos.append(orc)
    elementos.append(Spacer(1, 4))
    elementos.append(info)
    elementos.append(Spacer(1, 4))
    elementos.append(pag_info)
    elementos.append(Spacer(1, 14))


def _secao_titulo(elementos, texto, espaco_antes=6):
    p = Paragraph(
        texto,
        _style(f"tt-{texto}", fontName="Helvetica-Bold", fontSize=10,
               textColor=COR_TITULO),
    )
    elementos.append(Spacer(1, espaco_antes))
    elementos.append(p)
    elementos.append(Spacer(1, 6))


def _dados_cliente(elementos, orcamento):
    _secao_titulo(elementos, "DADOS DO CLIENTE")
    cliente = orcamento.atendimento.veiculo.cliente
    rows = [
        ("Nome", cliente.nome),
        ("CPF", cliente.cpf),
        ("Telefone", cliente.telefone),
        ("E-mail", cliente.email),
        ("Endereço", cliente.endereco),
    ]
    data = []
    for label, valor in rows:
        data.append([
            Paragraph(label, _style("l", fontName="Helvetica-Bold", fontSize=TAM_LABEL,
                                    textColor=COR_CINZA_ESCURO)),
            Paragraph(_valor(valor), _style("v", fontSize=TAM_VALOR)),
        ])
    t = Table(data, colWidths=[LARGURA_UTIL * 0.25, LARGURA_UTIL * 0.75], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elementos.append(t)
    elementos.append(Spacer(1, 10))


def _dados_veiculo(elementos, orcamento):
    _secao_titulo(elementos, "DADOS DO VEÍCULO", espaco_antes=4)
    veiculo = orcamento.atendimento.veiculo
    rows = [
        ("Marca", veiculo.marca),
        ("Modelo", veiculo.modelo),
        ("Placa", veiculo.placa),
        ("Ano", veiculo.ano),
        ("Cor", veiculo.cor),
    ]
    data = [
        [
            Paragraph(label, _style("l", fontName="Helvetica-Bold", fontSize=TAM_LABEL,
                                    textColor=COR_CINZA_ESCURO)),
            Paragraph(_valor(valor), _style("v", fontSize=TAM_VALOR)),
        ]
        for label, valor in rows
    ]
    t = Table(data, colWidths=[LARGURA_UTIL * 0.25, LARGURA_UTIL * 0.75], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elementos.append(t)
    elementos.append(Spacer(1, 10))


def _dados_servico(elementos, orcamento):
    _secao_titulo(elementos, "DADOS DO SERVIÇO", espaco_antes=4)
    atendimento = orcamento.atendimento
    data_entrada = (
        atendimento.data_entrada.strftime("%d/%m/%Y %H:%M")
        if atendimento.data_entrada
        else None
    )
    rows = [
        ("Data de entrada", data_entrada),
        ("Mecânico responsável", atendimento.mecanico_responsavel),
        ("Conferente", atendimento.conferente),
        ("Status do serviço", atendimento.status_descricao if atendimento.status else None),
    ]
    data = [
        [
            Paragraph(label, _style("l", fontName="Helvetica-Bold", fontSize=TAM_LABEL,
                                    textColor=COR_CINZA_ESCURO)),
            Paragraph(_valor(valor), _style("v", fontSize=TAM_VALOR)),
        ]
        for label, valor in rows
    ]
    t = Table(data, colWidths=[LARGURA_UTIL * 0.25, LARGURA_UTIL * 0.75], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elementos.append(t)
    elementos.append(Spacer(1, 10))


def _tabela_itens(elementos, orcamento):
    _secao_titulo(elementos, "ITENS DO ORÇAMENTO", espaco_antes=4)
    larguras = [LARGURA_UTIL * 5 / 10, LARGURA_UTIL * 1 / 10,
                LARGURA_UTIL * 2 / 10, LARGURA_UTIL * 2 / 10]
    data = [[
        Paragraph("Descrição", _style("h", fontName="Helvetica-Bold", fontSize=9,
                                      textColor=colors.white)),
        Paragraph("Qtd.", _style("h", fontName="Helvetica-Bold", fontSize=9,
                                 textColor=colors.white, alignment=TA_CENTER)),
        Paragraph("Valor unitário", _style("h", fontName="Helvetica-Bold", fontSize=9,
                                           textColor=colors.white, alignment=TA_RIGHT)),
        Paragraph("Subtotal", _style("h", fontName="Helvetica-Bold", fontSize=9,
                                     textColor=colors.white, alignment=TA_RIGHT)),
    ]]
    for item in orcamento.itens:
        data.append([
            Paragraph(_valor(item.descricao), _style("d", fontSize=9)),
            Paragraph(str(item.quantidade if item.quantidade is not None else 1),
                      _style("d", fontSize=9, alignment=TA_CENTER)),
            Paragraph(_moeda(item.valor_unitario), _style("d", fontSize=9, alignment=TA_RIGHT)),
            Paragraph(_moeda(item.subtotal), _style("d", fontSize=9, alignment=TA_RIGHT)),
        ])
    t = Table(data, colWidths=larguras, hAlign="LEFT")
    estilos = [
        ("BACKGROUND", (0, 0), (-1, 0), COR_CABECALHO_TABELA),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.Color(0.85, 0.85, 0.9)),
    ]
    for i in range(1, len(data)):
        if i % 2 == 1:
            estilos.append(("BACKGROUND", (0, i), (-1, i), COR_LINHA_ALTERNADA))
    t.setStyle(TableStyle(estilos))
    elementos.append(t)
    elementos.append(Spacer(1, 10))


def _totais(elementos, orcamento):
    largura_total = LARGURA_UTIL * 0.5
    data = [
        [Paragraph("Peças", _style("tp", fontSize=10)),
         Paragraph(_moeda(orcamento.valor_pecas), _style("tv", fontSize=10, alignment=TA_RIGHT))],
        [Paragraph("Mão de obra", _style("tp", fontSize=10)),
         Paragraph(_moeda(orcamento.valor_mao_de_obra), _style("tv", fontSize=10, alignment=TA_RIGHT))],
        [Paragraph("TOTAL", _style("tt", fontName="Helvetica-Bold", fontSize=12,
                                   textColor=COR_TITULO)),
         Paragraph(_moeda(orcamento.valor_total), _style("tt", fontName="Helvetica-Bold",
                                                         fontSize=12, textColor=COR_TITULO,
                                                         alignment=TA_RIGHT))],
    ]
    t = Table(data, colWidths=[largura_total * 0.5, largura_total * 0.5], hAlign="RIGHT")
    estilos = [
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, 2), (-1, 2), COR_DESTAQUE),
    ]
    t.setStyle(TableStyle(estilos))
    elementos.append(t)
    elementos.append(Spacer(1, 10))


def _plano_parcelas(elementos, orcamento):
    parcelas = list(orcamento.parcelas)
    if not parcelas:
        return
    _secao_titulo(elementos, "PLANO DE PARCELAS", espaco_antes=4)
    larguras = [
        LARGURA_UTIL * 2 / 10,
        LARGURA_UTIL * 2 / 10,
        LARGURA_UTIL * 2 / 10,
        LARGURA_UTIL * 2 / 10,
        LARGURA_UTIL * 2 / 10,
    ]
    data = [[
        Paragraph("Parcela", _style("h", fontName="Helvetica-Bold", fontSize=9,
                                    textColor=colors.white)),
        Paragraph("Vencimento", _style("h", fontName="Helvetica-Bold", fontSize=9,
                                       textColor=colors.white, alignment=TA_CENTER)),
        Paragraph("Valor", _style("h", fontName="Helvetica-Bold", fontSize=9,
                                  textColor=colors.white, alignment=TA_RIGHT)),
        Paragraph("Situação", _style("h", fontName="Helvetica-Bold", fontSize=9,
                                     textColor=colors.white, alignment=TA_CENTER)),
        Paragraph("Pago em", _style("h", fontName="Helvetica-Bold", fontSize=9,
                                    textColor=colors.white, alignment=TA_CENTER)),
    ]]
    pago_total = Decimal("0")
    for parcela in parcelas:
        if parcela.status_pagamento == "PAGO":
            pago_total += _dec(parcela.valor)
        data.append([
            Paragraph(parcela.rotulo, _style("d", fontSize=9)),
            Paragraph(
                parcela.vencimento.strftime("%d/%m/%Y") if parcela.vencimento else "—",
                _style("d", fontSize=9, alignment=TA_CENTER),
            ),
            Paragraph(_moeda(parcela.valor), _style("d", fontSize=9, alignment=TA_RIGHT)),
            Paragraph(parcela.status_pagamento_descricao,
                      _style("d", fontSize=9, alignment=TA_CENTER)),
            Paragraph(
                parcela.data_pagamento.strftime("%d/%m/%Y") if parcela.data_pagamento else "—",
                _style("d", fontSize=9, alignment=TA_CENTER),
            ),
        ])
    t = Table(data, colWidths=larguras, hAlign="LEFT")
    estilos = [
        ("BACKGROUND", (0, 0), (-1, 0), COR_CABECALHO_TABELA),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.Color(0.85, 0.85, 0.9)),
    ]
    for i in range(1, len(data)):
        if i % 2 == 1:
            estilos.append(("BACKGROUND", (0, i), (-1, i), COR_LINHA_ALTERNADA))
    t.setStyle(TableStyle(estilos))
    elementos.append(t)
    elementos.append(Spacer(1, 4))
    if pago_total > 0:
        p = Paragraph(
            f"Total já recebido: {_moeda(pago_total)}",
            _style("tp", fontName="Helvetica-Bold", fontSize=10),
        )
        elementos.append(p)
    elementos.append(Spacer(1, 10))


def _dec(valor):
    if valor is None:
        return Decimal("0")
    return Decimal(valor)


def _observacoes(elementos, orcamento):
    if not orcamento.observacoes or not orcamento.observacoes.strip():
        return
    _secao_titulo(elementos, "OBSERVAÇÕES", espaco_antes=4)
    p = Paragraph(orcamento.observacoes, _style("o", fontSize=10))
    elementos.append(p)
    elementos.append(Spacer(1, 10))


def _rodape(elementos):
    p = Paragraph(
        f"Documento gerado pelo JAPACAR em {date.today().strftime('%d/%m/%Y')}",
        _style("f", fontSize=8, textColor=COR_CINZA, alignment=TA_CENTER),
    )
    elementos.append(Spacer(1, 20))
    elementos.append(p)