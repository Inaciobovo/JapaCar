@extends('layouts.app')

@section('titulo', $cliente->exists ? 'Editar Cliente' : 'Novo Cliente')

@section('conteudo')
<div class="d-flex align-items-center mb-2">
    <a href="{{ route('clientes.index') }}" class="btn btn-sm btn-outline-secondary me-2 no-print">
        <i class="bi bi-arrow-left"></i>
    </a>
    <h1 class="page-title">{{ $cliente->exists ? 'Editar Cliente' : 'Novo Cliente' }}</h1>
</div>
<p class="page-subtitle">Preencha os dados do cliente</p>

@include('fragments.alerts')

<form action="{{ $cliente->exists ? route('clientes.update', $cliente) : route('clientes.store') }}"
      method="post" class="form-card">
    @csrf
    @if ($cliente->exists)
        @method('PUT')
    @endif

    <div class="mb-3">
        <label class="form-label-custom">Nome completo *</label>
        <input type="text" name="nome" value="{{ old('nome', $cliente->nome) }}" class="form-control" required maxlength="255"
               placeholder="Nome do cliente">
    </div>

    <div class="row">
        <div class="col-12 col-md-5 mb-3">
            <label class="form-label-custom">CPF</label>
            <input type="text" name="cpf" value="{{ old('cpf', $cliente->cpf) }}" class="form-control" data-mask="cpf"
                   maxlength="14" placeholder="000.000.000-00">
        </div>
        <div class="col-12 col-md-7 mb-3">
            <label class="form-label-custom">Telefone</label>
            <input type="text" name="telefone" value="{{ old('telefone', $cliente->telefone) }}" class="form-control"
                   data-mask="telefone" maxlength="15" placeholder="(00) 00000-0000">
        </div>
    </div>

    <div class="mb-3">
        <label class="form-label-custom">E-mail</label>
        <input type="email" name="email" value="{{ old('email', $cliente->email) }}" class="form-control"
               maxlength="255" placeholder="email@exemplo.com">
    </div>

    <div class="mb-3">
        <label class="form-label-custom">Endereço</label>
        <input type="text" name="endereco" value="{{ old('endereco', $cliente->endereco) }}" class="form-control"
               maxlength="255" placeholder="Rua, número, bairro, cidade">
    </div>

    @include('fragments.form-actions', ['actionLabel' => 'Salvar cliente', 'cancelarUrl' => route('clientes.index')])
</form>
@endsection
