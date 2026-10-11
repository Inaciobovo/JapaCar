@extends('layouts.app')

@section('titulo', 'Painel de Serviços')

@section('conteudo')
<div class="d-flex align-items-center justify-content-between mb-2">
    <div>
        <h1 class="page-title mb-0">Painel de Serviços</h1>
        <p class="page-subtitle mb-0">Acompanhe os veículos em atendimento na oficina</p>
    </div>
    <a href="{{ route('atendimentos.create') }}" class="btn btn-sm btn-japacar">
        <i class="bi bi-plus-lg me-1"></i> Novo
    </a>
</div>

@include('fragments.alerts')

<div class="search-bar">
    <a href="{{ route('atendimentos.index') }}" class="btn btn-sm btn-outline-secondary {{ $status === null ? 'active' : '' }}">Todos</a>
    <a href="{{ route('atendimentos.index', ['status' => 'EM_ANDAMENTO']) }}" class="btn btn-sm btn-outline-warning {{ $status === 'EM_ANDAMENTO' ? 'active' : '' }}">Em andamento</a>
    <a href="{{ route('atendimentos.index', ['status' => 'FINALIZADO']) }}" class="btn btn-sm btn-outline-success {{ $status === 'FINALIZADO' ? 'active' : '' }}">Finalizados</a>
</div>

@if ($atendimentos->isNotEmpty())
    <div class="row">
        @foreach ($atendimentos as $atendimento)
            <div class="col-12 col-lg-6">
                <div class="card-custom service-card">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div>
                            <div class="fw-bold">{{ $atendimento->veiculo->modelo }} {{ $atendimento->veiculo->marca }}</div>
                            <span class="text-uppercase fw-semibold text-muted">{{ $atendimento->veiculo->placa }}</span>
                        </div>
                        <span class="badge badge-status {{ $atendimento->finalizado() ? 'badge-concluido' : 'badge-em-andamento' }}">
                            {{ $atendimento->statusDescricao() }}
                        </span>
                    </div>

                    <div class="detail-list">
                        <div class="d-flex justify-content-between">
                            <span class="detail-label">Cliente</span>
                            <span class="fw-semibold">{{ $atendimento->veiculo->cliente->nome }}</span>
                        </div>
                        <div class="d-flex justify-content-between">
                            <span class="detail-label">Entrada</span>
                            <span>{{ $atendimento->created_at?->format('d/m/Y H:i') }}</span>
                        </div>
                        @if ($atendimento->checklistEntrada)
                            <div class="d-flex justify-content-between">
                                <span class="detail-label">Checklist</span>
                                <a href="{{ route('checklists.show', $atendimento->checklistEntrada) }}">#{{ $atendimento->checklistEntrada->id }}</a>
                            </div>
                        @endif
                        <div class="d-flex justify-content-between">
                            <span class="detail-label">Orçamentos</span>
                            <span>{{ $atendimento->orcamentos->count() }}</span>
                        </div>
                    </div>

                    <div class="d-flex gap-2 flex-wrap mt-3 no-print">
                        <a href="{{ route('atendimentos.show', $atendimento) }}" class="btn btn-sm btn-outline-secondary">
                            <i class="bi bi-eye me-1"></i> Abrir
                        </a>
                        <a href="{{ route('orcamentos.create', ['atendimento_id' => $atendimento->id]) }}" class="btn btn-sm btn-japacar">
                            <i class="bi bi-file-earmark-text me-1"></i> Orçamento
                        </a>
                        @if (! $atendimento->finalizado())
                            <form action="{{ route('atendimentos.finalizar', $atendimento) }}" method="post" class="d-inline">
                                @csrf
                                <button type="submit" class="btn btn-sm btn-outline-success">
                                    <i class="bi bi-check-lg me-1"></i> Finalizar
                                </button>
                            </form>
                        @endif
                    </div>
                </div>
            </div>
        @endforeach
    </div>
@else
    <div class="card-custom text-center py-5">
        <i class="bi bi-tools display-4 text-muted"></i>
        <p class="text-muted mt-3 mb-1">Nenhum serviço encontrado.</p>
        <p class="text-muted small mb-3">Abra um checklist e inicie um atendimento para o veículo.</p>
        <a href="{{ route('checklists.create') }}" class="btn btn-sm mt-1 btn-japacar">
            <i class="bi bi-clipboard-check me-1"></i> Abrir checklist de entrada
        </a>
    </div>
@endif

@if ($atendimentos->hasPages())
    <div class="mt-3">{{ $atendimentos->links('pagination::bootstrap-5') }}</div>
@endif
@endsection
