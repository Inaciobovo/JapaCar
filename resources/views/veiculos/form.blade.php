@extends('layouts.app')

@section('titulo', $veiculo->exists ? 'Editar veículo' : 'Novo veículo')

@section('conteudo')
<h1 class="h3 mb-4">{{ $veiculo->exists ? 'Editar veículo' : 'Novo veículo' }}</h1>

<form method="POST" action="{{ $veiculo->exists ? route('veiculos.update', $veiculo) : route('veiculos.store') }}">
    @csrf
    @if ($veiculo->exists)
        @method('PUT')
    @endif

    <div class="card p-4">
        <div class="row g-3">
            <div class="col-md-6">
                <label class="form-label">Cliente *</label>
                <select class="form-select" name="cliente_id" required>
                    <option value="">Selecione…</option>
                    @foreach ($clientes as $cliente)
                        <option value="{{ $cliente->id }}" @selected(old('cliente_id', $veiculo->cliente_id) == $cliente->id)>
                            {{ $cliente->nome }}
                        </option>
                    @endforeach
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label">Placa *</label>
                <input class="form-control text-uppercase" name="placa" value="{{ old('placa', $veiculo->placa) }}" required>
            </div>
            <div class="col-md-3">
                <label class="form-label">Ano</label>
                <input class="form-control" type="number" name="ano" value="{{ old('ano', $veiculo->ano) }}">
            </div>
            <div class="col-md-4">
                <label class="form-label">Marca *</label>
                <input class="form-control" name="marca" value="{{ old('marca', $veiculo->marca) }}" required>
            </div>
            <div class="col-md-4">
                <label class="form-label">Modelo *</label>
                <input class="form-control" name="modelo" value="{{ old('modelo', $veiculo->modelo) }}" required>
            </div>
            <div class="col-md-4">
                <label class="form-label">Cor</label>
                <input class="form-control" name="cor" value="{{ old('cor', $veiculo->cor) }}">
            </div>
        </div>
    </div>

    <div class="mt-3">
        <button class="btn btn-dark" type="submit">Salvar</button>
        <a class="btn btn-outline-secondary" href="{{ route('veiculos.index') }}">Cancelar</a>
    </div>
</form>
@endsection
