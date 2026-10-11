@extends('layouts.app')

@section('titulo', 'Orçamentos')

@section('conteudo')
<div class="d-flex align-items-center justify-content-between mb-2">
    <h1 class="page-title">Orçamentos</h1>
    <a href="{{ route('atendimentos.index') }}" class="btn btn-sm btn-japacar">
        <i class="bi bi-plus-lg me-1"></i> Novo
    </a>
</div>
<p class="page-subtitle">Orçamentos e estimativas de serviço</p>

@include('fragments.alerts')

<div class="search-bar">
    <a href="{{ route('orcamentos.index') }}" class="btn btn-sm btn-outline-secondary {{ $status === null ? 'active' : '' }}">Todos</a>
    <a href="{{ route('orcamentos.index', ['status' => 'PENDENTE']) }}" class="btn btn-sm btn-outline-warning {{ $status === 'PENDENTE' ? 'active' : '' }}">Pendentes</a>
    <a href="{{ route('orcamentos.index', ['status' => 'APROVADO']) }}" class="btn btn-sm btn-outline-success {{ $status === 'APROVADO' ? 'active' : '' }}">Aprovados</a>
    <a href="{{ route('orcamentos.index', ['status' => 'RECUSADO']) }}" class="btn btn-sm btn-outline-danger {{ $status === 'RECUSADO' ? 'active' : '' }}">Recusados</a>
</div>

@php
    $classeStatus = fn ($status) => match ($status) {
        'PENDENTE' => 'badge-pendente',
        'APROVADO' => 'badge-concluido',
        'RECUSADO' => 'badge-cancelado',
        default => 'badge-inativo',
    };
@endphp

@if ($orcamentos->isNotEmpty())
    <div class="table-responsive d-none d-lg-block">
        <table class="table table-hover">
            <thead>
            <tr>
                <th>Orçamento</th>
                <th>Veículo / Cliente</th>
                <th>Data</th>
                <th class="text-end">Valor</th>
                <th>Status</th>
                <th class="text-end">Ações</th>
            </tr>
            </thead>
            <tbody>
            @foreach ($orcamentos as $orcamento)
                <tr>
                    <td><div class="fw-semibold">#{{ $orcamento->id }}</div></td>
                    <td>
                        <div class="fw-semibold">{{ $orcamento->atendimento->veiculo->placa }} · {{ $orcamento->atendimento->veiculo->modelo }}</div>
                        <small class="text-muted">{{ $orcamento->atendimento->veiculo->cliente->nome }}</small>
                    </td>
                    <td>{{ $orcamento->created_at?->format('d/m/Y H:i') }}</td>
                    <td class="text-end fw-bold">R$ {{ number_format($orcamento->valor_total, 2, ',', '.') }}</td>
                    <td>
                        <span class="badge badge-status {{ $classeStatus($orcamento->status) }}">{{ $orcamento->statusDescricao() }}</span>
                    </td>
                    <td class="text-end text-nowrap">
                        <a href="{{ route('orcamentos.show', $orcamento) }}" class="btn btn-sm btn-outline-secondary" title="Abrir">
                            <i class="bi bi-eye"></i>
                        </a>
                        <a href="{{ route('orcamentos.pdf', $orcamento) }}" class="btn btn-sm btn-outline-danger" title="Baixar PDF">
                            <i class="bi bi-file-earmark-pdf"></i>
                        </a>
                    </td>
                </tr>
            @endforeach
            </tbody>
        </table>
    </div>
@endif

@if ($orcamentos->isNotEmpty())
    <div class="list-cards d-lg-none">
        @foreach ($orcamentos as $orcamento)
            <div class="list-card">
                <div class="lc-top">
                    <div class="lc-title">
                        <span>Orçamento #{{ $orcamento->id }}</span>
                        <small>{{ $orcamento->atendimento->veiculo->placa }} · {{ $orcamento->atendimento->veiculo->modelo }}</small>
                    </div>
                    <span class="badge badge-status {{ $classeStatus($orcamento->status) }}">{{ $orcamento->statusDescricao() }}</span>
                </div>
                <div class="lc-meta">
                    <span>Cliente</span>
                    <strong>{{ $orcamento->atendimento->veiculo->cliente->nome }}</strong>
                    <span>Data</span>
                    <strong>{{ $orcamento->created_at?->format('d/m/Y') }}</strong>
                    <span>Valor</span>
                    <strong class="fw-bold">R$ {{ number_format($orcamento->valor_total, 2, ',', '.') }}</strong>
                </div>
                <div class="lc-actions">
                    <a href="{{ route('orcamentos.show', $orcamento) }}" class="btn btn-sm btn-outline-secondary">
                        <i class="bi bi-eye me-1"></i> Abrir
                    </a>
                    <a href="{{ route('orcamentos.pdf', $orcamento) }}" class="btn btn-sm btn-outline-danger">
                        <i class="bi bi-file-earmark-pdf me-1"></i> PDF
                    </a>
                </div>
            </div>
        @endforeach
    </div>
@endif

@if ($orcamentos->isEmpty())
    <div class="card-custom text-center py-5">
        <i class="bi bi-file-earmark-text display-4 text-muted"></i>
        <p class="text-muted mt-3 mb-0">Nenhum orçamento encontrado.</p>
        <a href="{{ route('atendimentos.index') }}" class="btn btn-sm mt-3 btn-japacar">Ir para serviços</a>
    </div>
@endif

@if ($orcamentos->hasPages())
    <div class="mt-3">{{ $orcamentos->links('pagination::bootstrap-5') }}</div>
@endif
@endsection
