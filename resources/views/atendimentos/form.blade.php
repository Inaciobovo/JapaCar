@extends('layouts.app')

@section('titulo', 'Novo atendimento')

@section('conteudo')
<h1 class="h3 mb-4">Novo atendimento</h1>

<form method="POST" action="{{ route('atendimentos.store') }}">
    @csrf
    <div class="card p-4">
        <div class="row g-3">
            <div class="col-md-6">
                <label class="form-label">Veículo *</label>
                <select class="form-select" name="veiculo_id" required>
                    <option value="">Selecione…</option>
                    @foreach ($veiculos as $veiculo)
                        <option value="{{ $veiculo->id }}" @selected(old('veiculo_id', $atendimento->veiculo_id) == $veiculo->id)>
                            {{ $veiculo->placa }} — {{ $veiculo->marca }} {{ $veiculo->modelo }} ({{ $veiculo->cliente->nome }})
                        </option>
                    @endforeach
                </select>
            </div>
            <div class="col-md-6">
                <label class="form-label">Checklist de entrada (opcional)</label>
                <select class="form-select" name="checklist_entrada_id">
                    <option value="">—</option>
                    @foreach ($checklists as $checklist)
                        <option value="{{ $checklist->id }}" @selected(old('checklist_entrada_id') == $checklist->id)>
                            #{{ $checklist->id }} · {{ $checklist->data_entrada?->format('d/m/Y') }} · veículo {{ $checklist->veiculo_id }}
                        </option>
                    @endforeach
                </select>
            </div>
            <div class="col-12">
                <label class="form-label">Observações</label>
                <textarea class="form-control" name="observacoes" rows="3">{{ old('observacoes') }}</textarea>
            </div>
        </div>
    </div>

    <div class="mt-3">
        <button class="btn btn-dark" type="submit">Abrir atendimento</button>
        <a class="btn btn-outline-secondary" href="{{ route('atendimentos.index') }}">Cancelar</a>
    </div>
</form>
@endsection
