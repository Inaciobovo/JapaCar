@extends('layouts.app')

@section('titulo', 'Atendimento #'.$atendimento->id)

@section('conteudo')
<div class="d-flex justify-content-between align-items-start mb-3">
    <div>
        <h1 class="h3 mb-1">Atendimento #{{ $atendimento->id }}</h1>
        <div class="text-muted">
            <span class="badge bg-dark">{{ $atendimento->veiculo->placa }}</span>
            {{ $atendimento->veiculo->marca }} {{ $atendimento->veiculo->modelo }} ·
            {{ $atendimento->veiculo->cliente->nome }}
        </div>
    </div>
    <div class="text-end">
        <span class="badge bg-{{ $atendimento->finalizado() ? 'success' : 'warning' }} fs-6">
            {{ $atendimento->statusDescricao() }}
        </span>
        <div class="mt-2">
            <a class="btn btn-outline-secondary btn-sm" href="{{ route('veiculos.show', $atendimento->veiculo) }}">Ver veículo</a>
            <a class="btn btn-dark btn-sm" href="{{ route('orcamentos.create', ['atendimento_id' => $atendimento->id]) }}">Novo orçamento</a>
            @unless ($atendimento->finalizado())
                <form class="d-inline" method="POST" action="{{ route('atendimentos.finalizar', $atendimento) }}">
                    @csrf
                    <button class="btn btn-success btn-sm" type="submit">Finalizar</button>
                </form>
            @endunless
        </div>
    </div>
</div>

@if ($atendimento->observacoes)
    <div class="card p-3 mb-3">
        <strong>Observações</strong>
        <div>{{ $atendimento->observacoes }}</div>
    </div>
@endif

@if ($atendimento->checklistEntrada)
    <h2 class="h5">Checklist vinculado</h2>
    <div class="card p-3 mb-3">
        <div>
            <strong>{{ $atendimento->checklistEntrada->data_entrada?->format('d/m/Y H:i') }}</strong>
            <span class="text-muted">
                · {{ $atendimento->checklistEntrada->quilometragem ? number_format($atendimento->checklistEntrada->quilometragem, 0, ',', '.') . ' km' : '—' }}
                · {{ $atendimento->checklistEntrada->nivelCombustivelDescricao() ?? '—' }}
            </span>
        </div>
        @if ($atendimento->checklistEntrada->fotos->isNotEmpty())
            <div class="d-flex gap-2 flex-wrap mt-2">
                @foreach ($atendimento->checklistEntrada->fotos as $foto)
                    <img class="thumb" src="{{ route('checklists.fotos.arquivo', $foto) }}" alt="Foto">
                @endforeach
            </div>
        @endif
    </div>
@endif

<h2 class="h5">Orçamentos</h2>
@forelse ($atendimento->orcamentos as $orcamento)
    <div class="card p-3 mb-2">
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <a href="{{ route('orcamentos.show', $orcamento) }}"><strong>Orçamento #{{ $orcamento->id }}</strong></a>
                <span class="badge bg-secondary">{{ $orcamento->statusDescricao() }}</span>
                <span class="badge bg-{{ $orcamento->status_pagamento === 'PAGO' ? 'success' : ($orcamento->status_pagamento === 'PARCIAL' ? 'info' : 'secondary') }}">
                    {{ $orcamento->statusPagamentoDescricao() }}
                </span>
                <div class="text-muted small">{{ $orcamento->itens->count() }} item(ns)</div>
            </div>
            <div class="text-end">
                <div class="fs-5">R$ {{ number_format($orcamento->valor_total, 2, ',', '.') }}</div>
                <a class="btn btn-sm btn-outline-secondary" href="{{ route('orcamentos.show', $orcamento) }}">Abrir</a>
            </div>
        </div>
    </div>
@empty
    <p class="text-muted">Nenhum orçamento criado.</p>
@endforelse
@endsection
