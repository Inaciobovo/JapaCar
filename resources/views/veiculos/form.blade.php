@extends('layouts.app')

@section('titulo', $veiculo->exists ? 'Editar Veículo' : 'Novo Veículo')

@section('conteudo')
<div class="d-flex align-items-center mb-2">
    <a href="{{ route('veiculos.index') }}" class="btn btn-sm btn-outline-secondary me-2 no-print">
        <i class="bi bi-arrow-left"></i>
    </a>
    <h1 class="page-title">{{ $veiculo->exists ? 'Editar Veículo' : 'Novo Veículo' }}</h1>
</div>
<p class="page-subtitle">Preencha os dados do veículo</p>

@include('fragments.alerts')

<form action="{{ $veiculo->exists ? route('veiculos.update', $veiculo) : route('veiculos.store') }}"
      method="post" class="form-card">
    @csrf
    @if ($veiculo->exists)
        @method('PUT')
    @endif

    <div class="row">
        <div class="col-12 col-md-4 mb-3">
            <label class="form-label-custom">Placa *</label>
            <input type="text" name="placa" value="{{ old('placa', $veiculo->placa) }}" class="form-control text-uppercase"
                   data-mask="placa" maxlength="8" required placeholder="ABC-1234">
        </div>
        <div class="col-12 col-md-4 mb-3">
            <label class="form-label-custom">Marca *</label>
            <input type="text" name="marca" value="{{ old('marca', $veiculo->marca) }}" class="form-control" required maxlength="100"
                   placeholder="Ex: Volkswagen">
        </div>
        <div class="col-12 col-md-4 mb-3">
            <label class="form-label-custom">Modelo *</label>
            <input type="text" name="modelo" value="{{ old('modelo', $veiculo->modelo) }}" class="form-control" required maxlength="100"
                   placeholder="Ex: Gol 1.6">
        </div>
    </div>

    <div class="row">
        <div class="col-6 col-md-4 mb-3">
            <label class="form-label-custom">Ano</label>
            <input type="number" name="ano" value="{{ old('ano', $veiculo->ano) }}" class="form-control" min="1900" max="2100"
                   placeholder="2020">
        </div>
        <div class="col-6 col-md-4 mb-3">
            <label class="form-label-custom">Cor</label>
            <input type="text" name="cor" value="{{ old('cor', $veiculo->cor) }}" class="form-control" maxlength="50"
                   placeholder="Ex: Prata">
        </div>
        <div class="col-12 col-md-4 mb-3">
            <label class="form-label-custom">Cliente *</label>
            <select name="cliente_id" class="form-select" required>
                <option value="">Selecione o cliente...</option>
                @foreach ($clientes as $cliente)
                    <option value="{{ $cliente->id }}" @selected(old('cliente_id', $veiculo->cliente_id) == $cliente->id)>{{ $cliente->nome }}</option>
                @endforeach
            </select>
        </div>
    </div>

    @include('fragments.form-actions', ['actionLabel' => 'Salvar veículo', 'cancelarUrl' => route('veiculos.index')])
</form>
@endsection
