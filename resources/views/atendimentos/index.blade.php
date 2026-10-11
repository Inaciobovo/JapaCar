@extends('layouts.app')

@section('titulo', 'Atendimentos')

@section('conteudo')
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1 class="h3 mb-0">Atendimentos</h1>
    <a class="btn btn-dark" href="{{ route('atendimentos.create') }}">Novo atendimento</a>
</div>

<div class="btn-group mb-3">
    <a class="btn btn-outline-secondary {{ $status === null ? 'active' : '' }}" href="{{ route('atendimentos.index') }}">Todos</a>
    <a class="btn btn-outline-secondary {{ $status === 'EM_ANDAMENTO' ? 'active' : '' }}" href="{{ route('atendimentos.index', ['status' => 'EM_ANDAMENTO']) }}">Em andamento</a>
    <a class="btn btn-outline-secondary {{ $status === 'FINALIZADO' ? 'active' : '' }}" href="{{ route('atendimentos.index', ['status' => 'FINALIZADO']) }}">Finalizados</a>
</div>

<div class="card">
    <table class="table mb-0 align-middle">
        <thead>
        <tr>
            <th>#</th>
            <th>Veículo</th>
            <th>Cliente</th>
            <th>Status</th>
            <th>Aberto em</th>
            <th>Orçamentos</th>
            <th class="text-end">Ações</th>
        </tr>
        </thead>
        <tbody>
        @forelse ($atendimentos as $atendimento)
            <tr>
                <td>{{ $atendimento->id }}</td>
                <td>
                    <span class="badge bg-dark">{{ $atendimento->veiculo->placa }}</span>
                    <div class="text-muted small">{{ $atendimento->veiculo->marca }} {{ $atendimento->veiculo->modelo }}</div>
                </td>
                <td>{{ $atendimento->veiculo->cliente->nome }}</td>
                <td>
                    <span class="badge bg-{{ $atendimento->finalizado() ? 'success' : 'warning' }}">
                        {{ $atendimento->statusDescricao() }}
                    </span>
                </td>
                <td>{{ $atendimento->created_at?->format('d/m/Y H:i') }}</td>
                <td>{{ $atendimento->orcamentos->count() }}</td>
                <td class="text-end">
                    <a class="btn btn-sm btn-outline-secondary" href="{{ route('atendimentos.show', $atendimento) }}">Abrir</a>
                </td>
            </tr>
        @empty
            <tr><td colspan="7" class="text-center text-muted py-4">Nenhum atendimento encontrado.</td></tr>
        @endforelse
        </tbody>
    </table>
</div>

<div class="mt-3">{{ $atendimentos->links() }}</div>
@endsection
