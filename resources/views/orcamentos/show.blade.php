@extends('layouts.app')

@section('titulo', 'Orçamento #'.$orcamento->id)

@section('conteudo')
<div class="d-flex align-items-center justify-content-between mb-2 flex-wrap gap-2">
    <div class="d-flex align-items-center">
    <a href="{{ route('atendimentos.show', $orcamento->atendimento) }}" class="btn btn-sm btn-outline-secondary me-2 no-print">
        <i class="bi bi-arrow-left"></i>
    </a>
    <h1 class="page-title mb-0">Orçamento #{{ $orcamento->id }}</h1>
    @php
        $classeStatus = match ($orcamento->status) {
            'PENDENTE' => 'badge-pendente',
            'APROVADO' => 'badge-concluido',
            'RECUSADO' => 'badge-cancelado',
            default => 'badge-inativo',
        };
    @endphp
    <span class="badge badge-status ms-2 {{ $classeStatus }}">{{ $orcamento->statusDescricao() }}</span>
    </div>
    <a href="{{ route('orcamentos.pdf', $orcamento) }}" class="btn btn-sm btn-japacar no-print">
        <i class="bi bi-file-earmark-pdf me-1"></i> Baixar PDF
    </a>
</div>
<p class="page-subtitle">
    {{ $orcamento->atendimento->veiculo->placa }} - {{ $orcamento->atendimento->veiculo->modelo }} {{ $orcamento->atendimento->veiculo->marca }} ({{ $orcamento->atendimento->veiculo->cliente->nome }})
</p>

@include('fragments.alerts')

<div class="row">
    <div class="col-12 col-lg-7">
        <div class="card-custom">
            <h6 class="fw-bold mb-3"><i class="bi bi-list-check me-1"></i> Itens / peças</h6>
            <div class="table-responsive">
                <table class="table align-middle">
                    <thead>
                    <tr>
                        <th>Descrição</th>
                        <th class="text-end">Qtd</th>
                        <th class="text-end">Unitário</th>
                        <th class="text-end">Subtotal</th>
                        <th></th>
                    </tr>
                    </thead>
                    <tbody>
                    @forelse ($orcamento->itens as $item)
                        <tr>
                            <td>{{ $item->descricao }}</td>
                            <td class="text-end">{{ $item->quantidade }}</td>
                            <td class="text-end">R$ {{ number_format($item->valor_unitario, 2, ',', '.') }}</td>
                            <td class="text-end">R$ {{ number_format($item->subtotal, 2, ',', '.') }}</td>
                            <td class="text-end">
                                <form action="{{ route('orcamentos.itens.destroy', $item) }}" method="post">
                                    @csrf
                                    <button type="submit" class="btn btn-sm btn-outline-danger" title="Remover">
                                        <i class="bi bi-trash"></i>
                                    </button>
                                </form>
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="5" class="text-center text-muted py-3">Nenhum item adicionado.</td></tr>
                    @endforelse
                    </tbody>
                </table>
            </div>

            <h6 class="fw-bold mb-2 mt-3">Adicionar item</h6>
            <form action="{{ route('orcamentos.itens.store', $orcamento) }}" method="post">
                @csrf
                <div class="row g-2 align-items-end">
                    <div class="col-12 col-md-5">
                        <label class="form-label-custom">Descrição</label>
                        <input type="text" name="descricao" class="form-control" required placeholder="Descrição do item/serviço">
                    </div>
                    <div class="col-4 col-md-2">
                        <label class="form-label-custom">Qtd</label>
                        <input type="number" name="quantidade" class="form-control" min="1" value="1" required>
                    </div>
                    <div class="col-8 col-md-3">
                        <label class="form-label-custom">Valor unitário</label>
                        <input type="number" step="0.01" min="0" name="valor_unitario" class="form-control" required placeholder="R$ unitário">
                    </div>
                    <div class="col-12 col-md-2 d-grid">
                        <button type="submit" class="btn btn-outline-secondary">
                            <i class="bi bi-plus-lg me-1"></i> Add
                        </button>
                    </div>
                </div>
            </form>
        </div>
    </div>

    <div class="col-12 col-lg-5">
        <div class="card-custom">
            <h6 class="fw-bold mb-3"><i class="bi bi-calculator me-1"></i> Totais</h6>
            <ul class="detail-list">
                <li>
                    <span class="detail-label">Mão de obra</span>
                    <span class="detail-value">R$ {{ number_format($orcamento->valor_mao_de_obra, 2, ',', '.') }}</span>
                </li>
                <li>
                    <span class="detail-label">Peças</span>
                    <span class="detail-value">R$ {{ number_format($orcamento->valor_pecas, 2, ',', '.') }}</span>
                </li>
                <li>
                    <span class="detail-label">Total</span>
                    <span class="detail-value">R$ {{ number_format($orcamento->valor_total, 2, ',', '.') }}</span>
                </li>
                <li>
                    <span class="detail-label">Pago</span>
                    <span class="detail-value text-success">R$ {{ number_format($orcamento->valor_pago, 2, ',', '.') }}</span>
                </li>
                <li>
                    <span class="detail-label">Restante</span>
                    <span class="detail-value text-danger">R$ {{ number_format($orcamento->valorRestante(), 2, ',', '.') }}</span>
                </li>
            </ul>
            <div class="mt-2">
                <span class="badge badge-status {{ $orcamento->status_pagamento === 'PAGO' ? 'badge-concluido' : ($orcamento->status_pagamento === 'PARCIAL' ? 'badge-em-andamento' : 'badge-inativo') }}">
                    {{ $orcamento->statusPagamentoDescricao() }}
                </span>
                @if ($orcamento->formaPagamentoDescricao())
                    <span class="badge badge-status badge-inativo">{{ $orcamento->formaPagamentoDescricao() }}</span>
                @endif
                @if ($orcamento->data_pagamento)
                    <span class="badge badge-status badge-inativo">{{ $orcamento->data_pagamento->format('d/m/Y') }}</span>
                @endif
            </ul>
        </div>

        <div class="card-custom">
            <h6 class="fw-bold mb-3"><i class="bi bi-cash-coin me-1"></i> Registrar pagamento</h6>
            <form action="{{ route('orcamentos.pagamento', $orcamento) }}" method="post">
                @csrf
                <div class="mb-2">
                    <label class="form-label-custom">Valor pago (R$)</label>
                    <input type="number" step="0.01" min="0" name="valor_pago" class="form-control"
                           value="{{ old('valor_pago', $orcamento->valor_pago) }}" required>
                </div>
                <div class="mb-2">
                    <label class="form-label-custom">Forma de pagamento</label>
                    <select name="forma_pagamento" class="form-select" required>
                        @foreach (config('japacar.forma_pagamento') as $valor => $rotulo)
                            <option value="{{ $valor }}" @selected(old('forma_pagamento', $orcamento->forma_pagamento) == $valor)>{{ $rotulo }}</option>
                        @endforeach
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label-custom">Data</label>
                    <input type="date" name="data_pagamento" class="form-control"
                           value="{{ old('data_pagamento', $orcamento->data_pagamento?->format('Y-m-d') ?? now()->format('Y-m-d')) }}" required>
                </div>
                <button type="submit" class="btn btn-japacar w-100">Salvar pagamento</button>
            </form>
        </div>
    </div>
</div>
@endsection
