@extends('layouts.app')

@section('titulo', 'Clientes')

@section('conteudo')
<div class="d-flex align-items-center justify-content-between mb-2">
    <h1 class="page-title">Clientes</h1>
    <a href="{{ route('clientes.create') }}" class="btn btn-sm btn-japacar">
        <i class="bi bi-plus-lg me-1"></i> Novo
    </a>
</div>
<p class="page-subtitle">Cadastro e busca de clientes da oficina</p>

@include('fragments.alerts')

<form method="get" action="{{ route('clientes.index') }}" class="search-bar">
    <input type="text" name="q" value="{{ $busca }}" class="form-control"
           placeholder="Buscar por nome ou CPF...">
    <button class="btn btn-japacar-dark" type="submit">
        <i class="bi bi-search"></i>
    </button>
</form>

@if ($clientes->isNotEmpty())
    <div class="table-responsive d-none d-lg-block">
        <table class="table table-hover">
            <thead>
            <tr>
                <th>Nome</th>
                <th>CPF</th>
                <th>Telefone</th>
                <th>E-mail</th>
                <th class="text-end">Ações</th>
            </tr>
            </thead>
            <tbody>
            @foreach ($clientes as $cliente)
                <tr>
                    <td>
                        <div class="fw-semibold">{{ $cliente->nome }}</div>
                        @unless ($cliente->ativo)
                            <span class="badge badge-status badge-inativo">Inativo</span>
                        @endunless
                    </td>
                    <td>{{ $cliente->cpf ?: '-' }}</td>
                    <td>{{ $cliente->telefone ?: '-' }}</td>
                    <td>{{ $cliente->email ?: '-' }}</td>
                    <td class="text-end text-nowrap">
                        <a href="{{ route('clientes.edit', $cliente) }}"
                           class="btn btn-sm btn-outline-secondary" title="Editar">
                            <i class="bi bi-pencil"></i>
                        </a>
                        <form action="{{ route('clientes.inativar', $cliente) }}" method="post"
                              class="d-inline" data-confirm="{{ $cliente->ativo ? 'Inativar este cliente?' : 'Reativar este cliente?' }}">
                            @csrf
                            <button type="submit" class="btn btn-sm btn-outline-{{ $cliente->ativo ? 'danger' : 'success' }}"
                                    title="{{ $cliente->ativo ? 'Inativar' : 'Reativar' }}">
                                <i class="bi bi-person-{{ $cliente->ativo ? 'x' : 'check' }}"></i>
                            </button>
                        </form>
                    </td>
                </tr>
            @endforeach
            </tbody>
        </table>
    </div>
@endif

@if ($clientes->isNotEmpty())
    <div class="list-cards d-lg-none">
        @foreach ($clientes as $cliente)
            <div class="list-card">
                <div class="lc-top">
                    <div class="lc-title">{{ $cliente->nome }}</div>
                    <span class="fs-6 text-muted text-uppercase">{{ $cliente->cpf ?: '-' }}</span>
                </div>
                <div class="lc-meta">
                    <span>Telefone</span>
                    <strong>{{ $cliente->telefone ?: '-' }}</strong>
                    <span>E-mail</span>
                    <strong class="text-truncate">{{ $cliente->email ?: '-' }}</strong>
                </div>
                <div class="lc-actions">
                    <a href="{{ route('clientes.edit', $cliente) }}" class="btn btn-sm btn-outline-secondary">
                        <i class="bi bi-pencil me-1"></i> Editar
                    </a>
                    <form action="{{ route('clientes.inativar', $cliente) }}" method="post"
                          class="d-inline" data-confirm="{{ $cliente->ativo ? 'Inativar este cliente?' : 'Reativar este cliente?' }}">
                        @csrf
                        <button type="submit" class="btn btn-sm btn-outline-{{ $cliente->ativo ? 'danger' : 'success' }}">
                            <i class="bi bi-person-{{ $cliente->ativo ? 'x' : 'check' }} me-1"></i> {{ $cliente->ativo ? 'Inativar' : 'Reativar' }}
                        </button>
                    </form>
                </div>
            </div>
        @endforeach
    </div>
@endif

@if ($clientes->isEmpty())
    <div class="card-custom text-center py-5">
        <i class="bi bi-people display-4 text-muted"></i>
        <p class="text-muted mt-3 mb-0">
            @if ($busca) Nenhum cliente encontrado para "{{ $busca }}". @else Nenhum cliente cadastrado ainda. @endif
        </p>
        <a href="{{ route('clientes.create') }}" class="btn btn-sm mt-3 btn-japacar">Cadastrar cliente</a>
    </div>
@endif

@if ($clientes->hasPages())
    <div class="mt-3">{{ $clientes->links('pagination::bootstrap-5') }}</div>
@endif
@endsection
