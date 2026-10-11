@extends('layouts.app')

@section('titulo', 'Orçamento #'.$orcamento->id)

@section('conteudo')
<h1 class="h3 mb-1">Orçamento #{{ $orcamento->id }}</h1>
<p class="text-muted">
    <a href="{{ route('atendimentos.show', $orcamento->atendimento) }}">Atendimento #{{ $orcamento->atendimento->id }}</a> ·
    <span class="badge bg-dark">{{ $orcamento->atendimento->veiculo->placa }}</span>
    {{ $orcamento->atendimento->veiculo->marca }} {{ $orcamento->atendimento->veiculo->modelo }} ·
    {{ $orcamento->atendimento->veiculo->cliente->nome }}
</p>

<div class="row g-3">
    <div class="col-lg-7">
        <div class="card p-3">
            <h2 class="h6">Itens / peças</h2>
            <table class="table align-middle mb-2">
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
                            <form method="POST" action="{{ route('orcamentos.itens.destroy', $item) }}">
                                @csrf
                                <button class="btn btn-sm btn-outline-danger">Remover</button>
                            </form>
                        </td>
                    </tr>
                @empty
                    <tr><td colspan="5" class="text-center text-muted py-3">Nenhum item adicionado.</td></tr>
                @endforelse
                </tbody>
            </table>

            <form method="POST" action="{{ route('orcamentos.itens.store', $orcamento) }}" class="row g-2 align-items-end">
                @csrf
                <div class="col-md-5">
                    <label class="form-label mb-1">Descrição</label>
                    <input class="form-control" name="descricao" required>
                </div>
                <div class="col-md-2">
                    <label class="form-label mb-1">Qtd</label>
                    <input class="form-control" type="number" step="1" min="1" name="quantidade" value="1" required>
                </div>
                <div class="col-md-3">
                    <label class="form-label mb-1">Valor unitário</label>
                    <input class="form-control" type="number" step="0.01" min="0" name="valor_unitario" required>
                </div>
                <div class="col-md-2 d-grid">
                    <button class="btn btn-outline-dark" type="submit">Adicionar</button>
                </div>
            </form>
        </div>
    </div>

    <div class="col-lg-5">
        <div class="card p-3 mb-3">
            <h2 class="h6">Totais</h2>
            <div class="d-flex justify-content-between"><span>Mão de obra</span><span>R$ {{ number_format($orcamento->valor_mao_de_obra, 2, ',', '.') }}</span></div>
            <div class="d-flex justify-content-between"><span>Peças</span><span>R$ {{ number_format($orcamento->valor_pecas, 2, ',', '.') }}</span></div>
            <hr class="my-2">
            <div class="d-flex justify-content-between fw-bold"><span>Total</span><span>R$ {{ number_format($orcamento->valor_total, 2, ',', '.') }}</span></div>
            <div class="d-flex justify-content-between text-success"><span>Pago</span><span>R$ {{ number_format($orcamento->valor_pago, 2, ',', '.') }}</span></div>
            <div class="d-flex justify-content-between text-danger"><span>Restante</span><span>R$ {{ number_format($orcamento->valorRestante(), 2, ',', '.') }}</span></div>
            <div class="mt-2">
                <span class="badge bg-{{ $orcamento->status_pagamento === 'PAGO' ? 'success' : ($orcamento->status_pagamento === 'PARCIAL' ? 'info' : 'secondary') }}">
                    {{ $orcamento->statusPagamentoDescricao() }}
                </span>
                @if ($orcamento->formaPagamentoDescricao())
                    <span class="badge bg-light text-dark">{{ $orcamento->formaPagamentoDescricao() }}</span>
                @endif
                @if ($orcamento->data_pagamento)
                    <span class="badge bg-light text-dark">{{ $orcamento->data_pagamento->format('d/m/Y') }}</span>
                @endif
            </div>
        </div>

        <div class="card p-3">
            <h2 class="h6">Registrar pagamento</h2>
            <form method="POST" action="{{ route('orcamentos.pagamento', $orcamento) }}">
                @csrf
                <div class="mb-2">
                    <label class="form-label">Valor pago (R$)</label>
                    <input class="form-control" type="number" step="0.01" min="0" name="valor_pago"
                           value="{{ old('valor_pago', $orcamento->valor_pago) }}" required>
                </div>
                <div class="mb-2">
                    <label class="form-label">Forma de pagamento</label>
                    <select class="form-select" name="forma_pagamento" required>
                        @foreach (config('japacar.forma_pagamento') as $valor => $rotulo)
                            <option value="{{ $valor }}" @selected(old('forma_pagamento', $orcamento->forma_pagamento) == $valor)>{{ $rotulo }}</option>
                        @endforeach
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">Data</label>
                    <input class="form-control" type="date" name="data_pagamento"
                           value="{{ old('data_pagamento', $orcamento->data_pagamento?->format('Y-m-d') ?? now()->format('Y-m-d')) }}" required>
                </div>
                <button class="btn btn-dark w-100" type="submit">Salvar pagamento</button>
            </form>
        </div>
    </div>
</div>
@endsection
