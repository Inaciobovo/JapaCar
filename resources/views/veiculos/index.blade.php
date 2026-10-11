@extends('layouts.app')

@section('titulo', 'Veículos')

@section('conteudo')
<div class="d-flex align-items-center justify-content-between mb-2">
    <h1 class="page-title">Veículos</h1>
    <a href="{{ route('veiculos.create') }}" class="btn btn-sm btn-japacar">
        <i class="bi bi-plus-lg me-1"></i> Novo
    </a>
</div>
<p class="page-subtitle">Veículos dos clientes</p>

@include('fragments.alerts')

<form method="get" action="{{ route('veiculos.index') }}" class="search-bar">
    <input type="text" name="q" value="{{ $busca }}" class="form-control"
           placeholder="Buscar por placa, modelo, marca ou cliente...">
    <button class="btn btn-japacar-dark" type="submit">
        <i class="bi bi-search"></i>
    </button>
</form>

@if (! $isMobile && $veiculos->isNotEmpty())
    <div class="table-responsive">
        <table class="table table-hover">
            <thead>
            <tr>
                <th>Placa</th>
                <th>Modelo</th>
                <th>Marca</th>
                <th>Ano / Cor</th>
                <th>Cliente</th>
                <th class="text-end">Ações</th>
            </tr>
            </thead>
            <tbody>
            @foreach ($veiculos as $veiculo)
                <tr>
                    <td><span class="fw-semibold text-uppercase">{{ $veiculo->placa }}</span></td>
                    <td>{{ $veiculo->modelo }}</td>
                    <td>{{ $veiculo->marca }}</td>
                    <td>{{ $veiculo->ano ?? '-' }} / {{ $veiculo->cor ?: '-' }}</td>
                    <td>{{ $veiculo->cliente->nome }}</td>
                    <td class="text-end text-nowrap">
                        <a href="{{ route('veiculos.show', $veiculo) }}" class="btn btn-sm btn-outline-secondary" title="Abrir">
                            <i class="bi bi-eye"></i>
                        </a>
                        <a href="{{ route('veiculos.edit', $veiculo) }}" class="btn btn-sm btn-outline-secondary" title="Editar">
                            <i class="bi bi-pencil"></i>
                        </a>
                    </td>
                </tr>
            @endforeach
            </tbody>
        </table>
    </div>
@endif

@if ($isMobile && $veiculos->isNotEmpty())
    <div class="list-cards">
        @foreach ($veiculos as $veiculo)
            <div class="list-card">
                <div class="lc-top">
                    <div class="lc-title">
                        <span class="text-uppercase">{{ $veiculo->placa }}</span>
                        <small>{{ $veiculo->modelo }} · {{ $veiculo->marca }}</small>
                    </div>
                    <i class="bi bi-car-front fs-4" style="color:#e94560;"></i>
                </div>
                <div class="lc-meta">
                    <span>Ano / Cor</span>
                    <strong>{{ $veiculo->ano ?? '-' }} / {{ $veiculo->cor ?: '-' }}</strong>
                    <span>Cliente</span>
                    <strong>{{ $veiculo->cliente->nome }}</strong>
                </div>
                <div class="lc-actions">
                    <a href="{{ route('veiculos.show', $veiculo) }}" class="btn btn-sm btn-outline-secondary">
                        <i class="bi bi-eye me-1"></i> Abrir
                    </a>
                    <a href="{{ route('veiculos.edit', $veiculo) }}" class="btn btn-sm btn-outline-secondary">
                        <i class="bi bi-pencil me-1"></i> Editar
                    </a>
                </div>
            </div>
        @endforeach
    </div>
@endif

@if ($veiculos->isEmpty())
    <div class="card-custom text-center py-5">
        <i class="bi bi-car-front display-4 text-muted"></i>
        <p class="text-muted mt-3 mb-0">
            @if ($busca) Nenhum veículo encontrado para "{{ $busca }}". @else Nenhum veículo cadastrado ainda. @endif
        </p>
        <a href="{{ route('veiculos.create') }}" class="btn btn-sm mt-3 btn-japacar">Cadastrar veículo</a>
    </div>
@endif

@if ($veiculos->hasPages())
    <div class="mt-3">{{ $veiculos->links('pagination::bootstrap-5') }}</div>
@endif
@endsection
