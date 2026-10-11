@extends('layouts.app')

@section('titulo', 'Clientes')

@section('conteudo')
<div class="d-flex justify-content-between align-items-center mb-3">
    <h1 class="h3 mb-0">Clientes</h1>
    <a href="{{ route('clientes.create') }}" class="btn btn-dark">Novo cliente</a>
</div>

<form class="row g-2 mb-3" method="GET">
    <div class="col-auto">
        <input class="form-control" name="q" value="{{ $busca }}" placeholder="Nome, CPF ou telefone">
    </div>
    <div class="col-auto"><button class="btn btn-outline-secondary">Buscar</button></div>
</form>

<div class="card">
    <table class="table table-hover mb-0">
        <thead>
        <tr><th>Nome</th><th>CPF</th><th>Telefone</th><th>Situação</th><th class="text-end">Ações</th></tr>
        </thead>
        <tbody>
        @forelse ($clientes as $cliente)
            <tr>
                <td>{{ $cliente->nome }}</td>
                <td>{{ $cliente->cpf }}</td>
                <td>{{ $cliente->telefone }}</td>
                <td>
                    <span class="badge bg-{{ $cliente->ativo ? 'success' : 'secondary' }}">
                        {{ $cliente->ativo ? 'Ativo' : 'Inativo' }}
                    </span>
                </td>
                <td class="text-end">
                    <a class="btn btn-sm btn-outline-secondary" href="{{ route('clientes.edit', $cliente) }}">Editar</a>
                    <form class="d-inline" method="POST" action="{{ route('clientes.inativar', $cliente) }}">
                        @csrf
                        <button class="btn btn-sm btn-outline-{{ $cliente->ativo ? 'danger' : 'success' }}">
                            {{ $cliente->ativo ? 'Inativar' : 'Reativar' }}
                        </button>
                    </form>
                </td>
            </tr>
        @empty
            <tr><td colspan="5" class="text-center text-muted py-4">Nenhum cliente encontrado.</td></tr>
        @endforelse
        </tbody>
    </table>
</div>

<div class="mt-3">{{ $clientes->links() }}</div>
@endsection
