@extends('layouts.app')

@section('titulo', $checklist->exists ? 'Editar Checklist' : 'Checklist de Entrada')

@section('conteudo')
<div class="d-flex align-items-center mb-2">
    <a href="{{ route('checklists.index') }}" class="btn btn-sm btn-outline-secondary me-2 no-print">
        <i class="bi bi-arrow-left"></i>
    </a>
    <h1 class="page-title">{{ $checklist->exists ? 'Editar Checklist' : 'Checklist de Entrada' }}</h1>
</div>
<p class="page-subtitle">Registre as condições do veículo no momento da entrada</p>

@include('fragments.alerts')

<form action="{{ $checklist->exists ? route('checklists.update', $checklist) : route('checklists.store') }}"
      method="post" enctype="multipart/form-data" class="form-card">
    @csrf
    @if ($checklist->exists)
        @method('PUT')
    @endif

    <div class="mb-3">
        <label class="form-label-custom">Veículo *</label>
        <select name="veiculo_id" class="form-select" required>
            <option value="">Selecione o veículo...</option>
            @foreach ($veiculos as $veiculo)
                <option value="{{ $veiculo->id }}" @selected(old('veiculo_id', $checklist->veiculo_id) == $veiculo->id)>
                    {{ $veiculo->placa }} - {{ $veiculo->modelo }} {{ $veiculo->marca }} ({{ $veiculo->cliente->nome }})
                </option>
            @endforeach
        </select>
    </div>

    <div class="row">
        <div class="col-6 col-md-4 mb-3">
            <label class="form-label-custom">Quilometragem</label>
            <input type="number" name="quilometragem" value="{{ old('quilometragem', $checklist->quilometragem) }}"
                   class="form-control" min="0" placeholder="123456">
        </div>
        <div class="col-6 col-md-4 mb-3">
            <label class="form-label-custom">Nível de combustível</label>
            <select name="nivel_combustivel" class="form-select">
                <option value="">Selecione...</option>
                @foreach (config('japacar.nivel_combustivel') as $chave => $texto)
                    <option value="{{ $chave }}" @selected(old('nivel_combustivel', $checklist->nivel_combustivel) == $chave)>{{ $texto }}</option>
                @endforeach
            </select>
        </div>
        <div class="col-12 col-md-4 mb-3">
            <label class="form-label-custom">Responsável *</label>
            <input type="text" name="responsavel" value="{{ old('responsavel', $checklist->responsavel) }}"
                   class="form-control" required maxlength="255" placeholder="Nome do mecânico/atendente">
        </div>
    </div>

    <div class="mb-3">
        <label class="form-label-custom">Condições da lataria</label>
        <textarea name="condicoes_lataria" class="form-control" rows="3"
                  placeholder="Descreva riscos, amassados, arranhões, etc.">{{ old('condicoes_lataria', $checklist->condicoes_lataria) }}</textarea>
    </div>

    <div class="mb-3">
        <label class="form-label-custom">Observações gerais</label>
        <textarea name="observacoes_gerais" class="form-control" rows="3"
                  placeholder="Outras observações relevantes">{{ old('observacoes_gerais', $checklist->observacoes_gerais) }}</textarea>
    </div>

    @if ($checklist->exists && $checklist->fotos->isNotEmpty())
        <div class="mb-3">
            <label class="form-label-custom">Fotos existentes</label>
            <div class="photo-grid">
                @foreach ($checklist->fotos as $foto)
                    <div class="photo-item">
                        <img src="{{ route('checklists.fotos.arquivo', $foto) }}" alt="Foto">
                        <span class="remove-photo"
                              onclick="document.getElementById('remove-foto-{{ $foto->id }}').submit(); return false;">&times;</span>
                        <form id="remove-foto-{{ $foto->id }}" action="{{ route('checklists.fotos.destroy', $foto) }}" method="post">
                            @csrf
                        </form>
                    </div>
                @endforeach
            </div>
        </div>
    @endif

    <div class="mb-3">
        <label class="form-label-custom">Adicionar fotos (até 5)</label>
        <input type="file" name="fotos[]" class="form-control" accept="image/*" multiple data-max-count="5">
        <div class="form-text">Selecione até 5 fotos. Na edição, as novas fotos são adicionadas às existentes.</div>
    </div>

    @include('fragments.form-actions', ['actionLabel' => 'Salvar checklist', 'cancelarUrl' => route('checklists.index')])
</form>
@endsection
