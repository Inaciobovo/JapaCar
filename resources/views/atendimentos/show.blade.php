@extends('layouts.app')

@section('titulo', 'Serviço #'.$atendimento->id)

@section('conteudo')
<div class="d-flex align-items-center justify-content-between mb-2">
    <div class="d-flex align-items-center">
        <a href="{{ route('atendimentos.index') }}" class="btn btn-sm btn-outline-secondary me-2 no-print">
            <i class="bi bi-arrow-left"></i>
        </a>
        <h1 class="page-title mb-0">Serviço #{{ $atendimento->id }}</h1>
        <span class="badge badge-status ms-2 {{ $atendimento->finalizado() ? 'badge-concluido' : 'badge-em-andamento' }}">
            {{ $atendimento->statusDescricao() }}
        </span>
    </div>
    <div class="d-flex gap-2 no-print">
        @if (! $atendimento->finalizado())
            <form action="{{ route('atendimentos.finalizar', $atendimento) }}" method="post">
                @csrf
                <button type="submit" class="btn btn-sm btn-japacar">
                    <i class="bi bi-check-lg me-1"></i> Finalizar
                </button>
            </form>
        @endif
    </div>
</div>
<p class="page-subtitle">{{ $atendimento->veiculo->modelo }} {{ $atendimento->veiculo->marca }} · {{ $atendimento->veiculo->placa }}</p>

@include('fragments.alerts')

<div class="row">
    <div class="col-12 col-lg-7">
        <div class="card-custom">
            <h6 class="fw-bold mb-3"><i class="bi bi-tools me-1"></i> Dados do serviço</h6>
            <ul class="detail-list">
                <li>
                    <span class="detail-label">Cliente</span>
                    <span class="detail-value">{{ $atendimento->veiculo->cliente->nome }}</span>
                </li>
                <li>
                    <span class="detail-label">Veículo</span>
                    <span class="detail-value">{{ $atendimento->veiculo->modelo }} {{ $atendimento->veiculo->marca }} · {{ $atendimento->veiculo->placa }}</span>
                </li>
                <li>
                    <span class="detail-label">Data de entrada</span>
                    <span class="detail-value">{{ $atendimento->created_at?->format('d/m/Y H:i') }}</span>
                </li>
                @if ($atendimento->data_finalizacao)
                    <li>
                        <span class="detail-label">Data de finalização</span>
                        <span class="detail-value">{{ $atendimento->data_finalizacao?->format('d/m/Y H:i') }}</span>
                    </li>
                @endif
                @if ($atendimento->checklistEntrada)
                    <li>
                        <span class="detail-label">Checklist vinculado</span>
                        <span class="detail-value">
                            <a href="{{ route('checklists.show', $atendimento->checklistEntrada) }}">#{{ $atendimento->checklistEntrada->id }}</a>
                        </span>
                    </li>
                @endif
            </ul>

            <h6 class="fw-bold mt-3 mb-2">Observações</h6>
            <p class="mb-0">{{ $atendimento->observacoes ?: '— Sem observações —' }}</p>
        </div>
    </div>

    <div class="col-12 col-lg-5">
        <div class="card-custom">
            <h6 class="fw-bold mb-3"><i class="bi bi-file-earmark-text me-1"></i> Orçamentos</h6>
            @forelse ($atendimento->orcamentos as $orcamento)
                <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                    <div>
                        <a href="{{ route('orcamentos.show', $orcamento) }}" class="fw-semibold text-decoration-none">Orçamento #{{ $orcamento->id }}</a>
                        <div class="text-muted small">R$ {{ number_format($orcamento->valor_total, 2, ',', '.') }}</div>
                        <span class="badge badge-status {{ $orcamento->status === 'APROVADO' ? 'badge-concluido' : ($orcamento->status === 'RECUSADO' ? 'badge-inativo' : 'badge-em-andamento') }}">
                            {{ $orcamento->statusDescricao() }}
                        </span>
                        <span class="badge badge-status {{ $orcamento->status_pagamento === 'PAGO' ? 'badge-concluido' : 'badge-inativo' }}">
                            {{ $orcamento->statusPagamentoDescricao() }}
                        </span>
                    </div>
                    <a href="{{ route('orcamentos.show', $orcamento) }}" class="btn btn-sm btn-outline-secondary">Abrir</a>
                </div>
            @empty
                <p class="text-muted small mb-3">Nenhum orçamento vinculado a este serviço.</p>
            @endforelse

            @if (! $atendimento->finalizado())
                <a href="{{ route('orcamentos.create', ['atendimento_id' => $atendimento->id]) }}" class="btn btn-sm btn-japacar w-100 mt-3">
                    <i class="bi bi-plus-lg me-1"></i> Adicionar orçamento
                </a>
            @endif
        </div>
    </div>
</div>
@endsection
