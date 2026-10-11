<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <style>
        * { font-family: DejaVu Sans, sans-serif; }
        body { color: #222; font-size: 12px; margin: 0; }
        .header { width: 100%; border-bottom: 3px solid #e94560; padding-bottom: 12px; margin-bottom: 16px; }
        .brand {
            font-size: 26px;
            font-weight: bold;
            color: #e94560;
            letter-spacing: 1px;
        }
        .brand-sub {
            font-size: 11px;
            color: #666;
        }
        .doc-title {
            text-align: right;
            font-size: 18px;
            font-weight: bold;
            color: #1a1a2e;
        }
        .muted { color: #777; }
        .small { font-size: 11px; }
        .section {
            border: 1px solid #e2e4ea;
            border-radius: 8px;
            padding: 10px 12px;
            margin-bottom: 12px;
        }
        .section h3 {
            margin: 0 0 6px;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #898989;
            font-weight: 700;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        .info td {
            padding: 2px 0;
            vertical-align: top;
            font-size: 0.9em;
        }
        .items th {
            background: #f4f5f9;
            border-bottom: 2px solid #e2e4e9;
            padding: 8px 6px;
            text-align: left;
            font-size: 0.8em;
            text-transform: uppercase;
            color: #555;
        }
        .items td {
            padding: 8px 6px;
            border-bottom: 1px solid #eee;
            font-size: 0.92em;
        }
        .text-end { text-align: right; }
        .totals {
            width: 60%;
            margin-left: 40%;
            border-collapse: collapse;
        }
        .totals td {
            padding: 6px 8px;
            font-size: 0.95em;
        }
        .totals tr.grand td {
            border-top: 2px solid #333;
            font-weight: bold;
            font-size: 1.05em;
        }
        .badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 0.78em;
            font-weight: bold;
            background: #e2e4e9;
            color: #333;
        }
        .footer {
            position: fixed;
            bottom: -20px;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 0.72em;
            color: #999;
            border-top: 1px solid #eee;
            padding-top: 6px;
        }
        .signatures {
            margin-top: 40px;
            width: 100%;
        }
        .signatures td {
            text-align: center;
            padding-top: 28px;
            border-top: 1px solid #aaa;
            width: 45%;
            font-size: 0.82em;
            color: #555;
        }
    </style>
</head>
<body>
    @php
        $oficina = config('japacar.oficina');
        $cliente = $orcamento->atendimento->veiculo->cliente;
        $veiculo = $orcamento->atendimento->veiculo;
    @endphp

    <table style="width:100%;">
        <tr>
            <td style="vertical-align:top;">
                <div style="font-size:1.5em;font-weight:bold;color:#e94560;">{{ $oficina['nome'] }}</div>
                <div style="color:#777;font-size:0.82em;">{{ $oficina['subtitulo'] }}</div>
                @if ($oficina['telefone'])
                    <div style="color:#777;font-size:0.82em;">Tel: {{ $oficina['telefone'] }}</div>
                @endif
                @if ($oficina['endereco'])
                    <div style="color:#777;font-size:0.82em;">{{ $oficina['endereco'] }}</div>
                @endif
            </td>
            <td style="vertical-align:top;text-align:right;">
                <div style="font-size:1.25em;font-weight:bold;">ORÇAMENTO #{{ $orcamento->id }}</div>
                <div style="color:#777;font-size:0.82em;">{{ $orcamento->created_at?->format('d/m/Y H:i') }}</div>
                <div style="margin-top:4px;">
                    <span class="badge">{{ $orcamento->statusDescricao() }}</span>
                </div>
            </td>
        </tr>
    </table>

    <div style="border-top:2px solid #eee;margin:12px 0;"></div>

    <table style="width:100%;border-collapse:separate;border-spacing:10px 0;margin:0 -10px;">
        <tr>
            <td style="width:50%;vertical-align:top;background:#fafbfc;border:1px solid #e8e9ee;border-radius:8px;padding:10px;">
                <div style="font-size:0.72em;text-transform:uppercase;letter-spacing:1px;color:#999;margin-bottom:6px;">Cliente</div>
                <div style="font-weight:bold;font-size:1em;">{{ $cliente->nome }}</div>
                @if ($cliente->cpf)<div style="font-size:0.85em;color:#555;">CPF: {{ $cliente->cpf }}</div>@endif
                @if ($cliente->telefone)<div style="font-size:0.85em;color:#555;">Telefone: {{ $cliente->telefone }}</div>@endif
                @if ($cliente->email)<div style="font-size:0.85em;color:#555;">E-mail: {{ $cliente->email }}</div>@endif
            </td>
            <td style="width:50%;vertical-align:top;background:#fafbfc;border:1px solid #e8e9ee;border-radius:8px;padding:10px;">
                <div style="font-size:0.72em;text-transform:uppercase;letter-spacing:1px;color:#999;margin-bottom:6px;">Veículo</div>
                <div style="font-weight:bold;font-size:1em;">{{ $veiculo->modelo }} {{ $veiculo->marca }}</div>
                <div style="font-size:0.85em;color:#555;">Placa: {{ $veiculo->placa }}</div>
                @if ($veiculo->ano)<div style="font-size:0.85em;color:#555;">Ano: {{ $veiculo->ano }}</div>@endif
                @if ($veiculo->cor)<div style="font-size:0.85em;color:#555;">Cor: {{ $veiculo->cor }}</div>@endif
            </td>
        </tr>
    </table>

    <div style="height:14px;"></div>

    <table class="items">
        <thead>
            <tr>
                <th>Descrição</th>
                <th class="text-end" style="width:60px;">Qtd</th>
                <th class="text-end" style="width:110px;">Unitário</th>
                <th class="text-end" style="width:110px;">Subtotal</th>
            </tr>
        </thead>
        <tbody>
            @forelse ($orcamento->itens as $item)
                <tr>
                    <td>{{ $item->descricao }}</td>
                    <td class="text-end">{{ $item->quantidade }}</td>
                    <td class="text-end">R$ {{ number_format($item->valor_unitario, 2, ',', '.') }}</td>
                    <td class="text-end">R$ {{ number_format($item->subtotal, 2, ',', '.') }}</td>
                </tr>
            @empty
                <tr><td colspan="4" style="text-align:center;color:#999;padding:14px;">Nenhum item de peça/serviço adicionado.</td></tr>
            @endforelse
        </tbody>
    </table>

    <div style="height:16px;"></div>

    <table class="totals">
        <tr>
            <td>Mão de obra</td>
            <td class="text-end">R$ {{ number_format($orcamento->valor_mao_de_obra, 2, ',', '.') }}</td>
        </tr>
        <tr>
            <td>Peças</td>
            <td class="text-end">R$ {{ number_format($orcamento->valor_pecas, 2, ',', '.') }}</td>
        </tr>
        <tr class="grand">
            <td>TOTAL</td>
            <td class="text-end">R$ {{ number_format($orcamento->valor_total, 2, ',', '.') }}</td>
        </tr>
        @if ((float) $orcamento->valor_pago > 0)
            <tr>
                <td>Pago ({{ $orcamento->formaPagamentoDescricao() }})</td>
                <td class="text-end" style="color:#28a745;">- R$ {{ number_format($orcamento->valor_pago, 2, ',', '.') }}</td>
            </tr>
            <tr>
                <td>Restante</td>
                <td class="text-end" style="font-weight:bold;color:#c0392b;">R$ {{ number_format($orcamento->valorRestante(), 2, ',', '.') }}</td>
            </tr>
        @endif
    </table>

    @if ($orcamento->observacoes)
        <div style="margin-top:22px;">
            <div style="font-size:0.72em;text-transform:uppercase;letter-spacing:1px;color:#999;margin-bottom:4px;">Observações</div>
            <div style="font-size:0.9em;color:#444;">{{ $orcamento->observacoes }}</div>
        </div>
    @endif

    <div style="margin-top:24px;font-size:0.82em;color:#666;">
        Validade do orçamento: 15 dias a partir da data de emissão.
    </div>

    <table class="signatures">
        <tr>
            <td style="padding-right:20px;">Assinatura do cliente</td>
            <td style="padding-left:20px;">{{ $oficina['nome'] }}</td>
        </tr>
    </table>

    <div class="footer">
        {{ $oficina['nome'] }} · Orçamento #{{ $orcamento->id }} · {{ $orcamento->created_at?->format('d/m/Y') }} · {{ $orcamento->statusDescricao() }}
    </div>
</body>
</html>
