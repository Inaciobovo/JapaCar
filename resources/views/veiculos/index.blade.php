@extends('layouts.app')

@section('titulo', 'Veículos')

@section('conteudo')
<div class="d-flex justify-content-between align-items-center mb-3">
    <h1 class="h3 mb-0">Veículos</h1>
    <a href="{{ route('veiculos.create') }}" class="btn btn-dark">Novo veículo</a>
</div>

<form class="row g-2 mb-3" method="GET">
    <div class="col-auto">
        <input class="form-control" name="q" value="{{ $busca }}" placeholder="Placa, modelo, marca ou cliente">
    </div>
    <div class="col-auto"><button class="btn btn-outline-secondary">Buscar</button></div>
</form>

<div class="card">
    <table class="table table-hover mb-0">
        <thead>
        <tr><th>Placa</th><th>Veículo</th><th>Cliente</th><th class="text-end">Ações</th></tr>
        </thead>
        <tbody>
        @forelse ($veiculos as $veiculo)
            <tr>
                <td><span class="badge bg-dark">{{ $veiculo->placa }}</span></td>
                <td>{{ $veiculo->marca }} {{ $veiculo->modelo }} @if($veiculo->ano) ({{ $veiculo->ano }}) @endif</td>
                <td>{{ $veiculo->cliente->nome }}</td>
                <td class="text-end">
                    <a class="btn btn-sm btn-outline-secondary" href="{{ route('veiculos.show', $veiculo) }}">Abrir</a>
                    <a class="btn btn-sm btn-outline-secondary" href="{{ route('veiculos.edit', $veiculo) }}">Editar</a>
                </td>
            </tr>
        @empty
            <tr><td colspan="4" class="text-center text-muted py-4">Nenhum veículo encontrado.</td></tr>
        @endforelse
        </tbody>
    </table>
</div>

<div class="mt-3">{{ $veiculos->links() }}</div>
@endsection
