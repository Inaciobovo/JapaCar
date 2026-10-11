@extends('layouts.app')

@section('titulo', $checklist->exists ? 'Editar checklist' : 'Novo checklist')

@section('conteudo')
<h1 class="h3 mb-4">{{ $checklist->exists ? 'Editar checklist' : 'Novo checklist' }}</h1>

<form method="POST"
      enctype="multipart/form-data"
      action="{{ $checklist->exists ? route('checklists.update', $checklist) : route('checklists.store') }}">
    @csrf
    @if ($checklist->exists)
        @method('PUT')
    @endif

    <div class="card p-4">
        <div class="row g-3">
            <div class="col-md-6">
                <label class="form-label">Veículo *</label>
                <select class="form-select" name="veiculo_id" required>
                    <option value="">Selecione…</option>
                    @foreach ($veiculos as $veiculo)
                        <option value="{{ $veiculo->id }}" @selected(old('veiculo_id', $checklist->veiculo_id) == $veiculo->id)>
                            {{ $veiculo->placa }} — {{ $veiculo->marca }} {{ $veiculo->modelo }} ({{ $veiculo->cliente->nome }})
                        </option>
                    @endforeach
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label">Data de entrada *</label>
                <input class="form-control" type="datetime-local" name="data_entrada"
                       value="{{ old('data_entrada', $checklist->data_entrada?->format('Y-m-d\TH:i')) }}" required>
            </div>
            <div class="col-md-3">
                <label class="form-label">Quilometragem</label>
                <input class="form-control" type="number" name="quilometragem"
                       value="{{ old('quilometragem', $checklist->quilometragem) }}">
            </div>
            <div class="col-md-4">
                <label class="form-label">Nível de combustível</label>
                <select class="form-select" name="nivel_combustivel">
                    <option value="">—</option>
                    @foreach (config('japacar.nivel_combustivel') as $valor => $rotulo)
                        <option value="{{ $valor }}" @selected(old('nivel_combustivel', $checklist->nivel_combustivel) == $valor)>
                            {{ $rotulo }}
                        </option>
                    @endforeach
                </select>
            </div>
            <div class="col-md-8">
                <label class="form-label">Responsável</label>
                <input class="form-control" name="responsavel" value="{{ old('responsavel', $checklist->responsavel) }}">
            </div>
            <div class="col-md-6">
                <label class="form-label">Condições da lataria</label>
                <textarea class="form-control" name="condicoes_lataria" rows="3">{{ old('condicoes_lataria', $checklist->condicoes_lataria) }}</textarea>
            </div>
            <div class="col-md-6">
                <label class="form-label">Observações gerais</label>
                <textarea class="form-control" name="observacoes_gerais" rows="3">{{ old('observacoes_gerais', $checklist->observacoes_gerais) }}</textarea>
            </div>
            <div class="col-12">
                <label class="form-label">Fotos</label>
                <input class="form-control" type="file" name="fotos[]" accept="image/*" multiple>
                <div class="form-text">JPG, PNG ou WEBP, até 5&nbsp;MB cada.</div>
            </div>
        </div>
    </div>

    <div class="mt-3">
        <button class="btn btn-dark" type="submit">Salvar</button>
        <a class="btn btn-outline-secondary" href="{{ route('checklists.index') }}">Cancelar</a>
    </div>
</form>

@if ($checklist->exists && $checklist->fotos->isNotEmpty())
    <h2 class="h5 mt-4">Fotos atuais</h2>
    <div class="d-flex gap-3 flex-wrap">
        @foreach ($checklist->fotos as $foto)
            <div class="text-center">
                <img class="thumb d-block mb-1" src="{{ route('checklists.fotos.arquivo', $foto) }}" alt="Foto">
                <form method="POST" action="{{ route('checklists.fotos.destroy', $foto) }}">
                    @csrf
                    <button class="btn btn-sm btn-outline-danger">Remover</button>
                </form>
            </div>
        @endforeach
    </div>
@endif
@endsection
