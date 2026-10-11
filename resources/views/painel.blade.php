@extends('layouts.app')

@section('titulo', 'Painel')

@section('conteudo')
<div class="welcome d-flex align-items-center justify-content-between mb-3">
    <div>
        <h1 class="page-title mb-0">Bem-vindo!</h1>
        <p class="page-subtitle mb-0">{{ auth()->user()->login }}</p>
    </div>
    <span class="d-none d-sm-block badge badge-brand">Oficina JAPACAR</span>
</div>

@include('fragments.alerts')

<div class="quick-actions">
    <a href="{{ route('checklists.create') }}" class="quick-action">
        <span class="qa-icon green"><i class="bi bi-clipboard-check"></i></span>
        <span class="qa-label">Novo Checklist</span>
    </a>
    <a href="{{ route('atendimentos.create') }}" class="quick-action">
        <span class="qa-icon blue"><i class="bi bi-tools"></i></span>
        <span class="qa-label">Novo Atendimento</span>
    </a>
    <a href="{{ route('clientes.create') }}" class="quick-action">
        <span class="qa-icon purple"><i class="bi bi-person-plus"></i></span>
        <span class="qa-label">Novo Cliente</span>
    </a>
    <a href="{{ route('veiculos.create') }}" class="quick-action">
        <span class="qa-icon teal"><i class="bi bi-car-front"></i></span>
        <span class="qa-label">Novo Veículo</span>
    </a>
    <a href="{{ route('atendimentos.index') }}" class="quick-action">
        <span class="qa-icon indigo"><i class="bi bi-wrench-adjustable"></i></span>
        <span class="qa-label">Painel de Serviços</span>
    </a>
    <a href="{{ route('orcamentos.index') }}" class="quick-action">
        <span class="qa-icon orange"><i class="bi bi-file-earmark-text"></i></span>
        <span class="qa-label">Orçamentos</span>
    </a>
</div>

<div class="stats-grid">
    <div class="stat-card">
        <span class="stat-label">Clientes ativos</span>
        <span class="stat-value">{{ $totalClientes }}</span>
    </div>
    <div class="stat-card">
        <span class="stat-label">Veículos</span>
        <span class="stat-value">{{ $totalVeiculos }}</span>
    </div>
    <div class="stat-card">
        <span class="stat-label">Checklists</span>
        <span class="stat-value">{{ $totalChecklists }}</span>
    </div>
    <div class="stat-card">
        <span class="stat-label">Em andamento</span>
        <span class="stat-value saldo">{{ $atendimentosAbertos }}</span>
    </div>
    <div class="stat-card">
        <span class="stat-label">Orçamentos pendentes</span>
        <span class="stat-value">{{ $orcamentosPendentes }}</span>
    </div>
</div>

<div class="row">
    <div class="col-12">
        @if ($atendimentos->isEmpty())
            <div class="card-custom text-center py-5">
                <i class="bi bi-tools display-4 text-muted"></i>
                <p class="text-muted mt-3 mb-0">Nenhum atendimento em andamento.</p>
                <a href="{{ route('checklists.create') }}" class="btn btn-sm mt-3 btn-japacar">Abrir checklist de entrada</a>
            </div>
        @else
            <div class="card-custom">
                <h6 class="fw-bold mb-3"><i class="bi bi-tools me-1"></i> Atendimentos em andamento</h6>
                <div class="list-group list-group-flush">
                    @foreach ($atendimentos as $atendimento)
                        <a href="{{ route('atendimentos.show', $atendimento) }}"
                           class="list-group-item list-group-item-action d-flex justify-content-between align-items-center px-0">
                            <div>
                                <div class="fw-semibold">{{ $atendimento->veiculo->modelo }} {{ $atendimento->veiculo->marca }}</div>
                                <small class="text-muted">{{ $atendimento->veiculo->placa }} · {{ $atendimento->veiculo->cliente->nome }}</small>
                            </div>
                            <span class="badge badge-status badge-em-andamento">Em andamento</span>
                        </a>
                    @endforeach
                </div>
            </div>
        @endif
    </div>
</div>
@endsection
