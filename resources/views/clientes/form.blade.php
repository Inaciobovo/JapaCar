@extends('layouts.app')

@section('titulo', $cliente->exists ? 'Editar cliente' : 'Novo cliente')

@section('conteudo')
<h1 class="h3 mb-4">{{ $cliente->exists ? 'Editar cliente' : 'Novo cliente' }}</h1>

<form method="POST" action="{{ $cliente->exists ? route('clientes.update', $cliente) : route('clientes.store') }}">
    @csrf
    @if ($cliente->exists)
        @method('PUT')
    @endif

    <div class="card p-4">
        <div class="row g-3">
            <div class="col-md-6">
                <label class="form-label">Nome *</label>
                <input class="form-control" name="nome" value="{{ old('nome', $cliente->nome) }}" required>
            </div>
            <div class="col-md-3">
                <label class="form-label">CPF</label>
                <input class="form-control" name="cpf" value="{{ old('cpf', $cliente->cpf) }}">
            </div>
            <div class="col-md-3">
                <label class="form-label">Telefone</label>
                <input class="form-control" name="telefone" value="{{ old('telefone', $cliente->telefone) }}">
            </div>
            <div class="col-md-6">
                <label class="form-label">E-mail</label>
                <input class="form-control" type="email" name="email" value="{{ old('email', $cliente->email) }}">
            </div>
            <div class="col-md-6">
                <label class="form-label">Endereço</label>
                <input class="form-control" name="endereco" value="{{ old('endereco', $cliente->endereco) }}">
            </div>
        </div>
    </div>

    <div class="mt-3">
        <button class="btn btn-dark" type="submit">Salvar</button>
        <a class="btn btn-outline-secondary" href="{{ route('clientes.index') }}">Cancelar</a>
    </div>
</form>
@endsection
