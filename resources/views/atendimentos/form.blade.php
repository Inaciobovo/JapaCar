@extends('layouts.app')

@section('titulo', 'Novo Atendimento')

@section('conteudo')
<div class="d-flex align-items-center mb-2">
    <a href="{{ route('atendimentos.index') }}" class="btn btn-sm btn-outline-secondary me-2 no-print">
        <i class="bi bi-arrow-left"></i>
    </a>
    <h1 class="page-title">Novo Atendimento</h1>
</div>
<p class="page-subtitle">Abra um serviço para o veículo do cliente</p>

@include('fragments.alerts')

<form action="{{ route('atendimentos.store') }}" method="post" class="form-card">
    @csrf

    <div class="mb-3">
        <label class="form-label-custom">Veículo *</label>
        <select name="veiculo_id" class="form-select" required>
            <option value="">Selecione o veículo...</option>
            @foreach ($veiculos as $veiculo)
                <option value="{{ $veiculo->id }}" @selected(old('veiculo_id', $atendimento->veiculo_id) == $veiculo->id)>
                    {{ $veiculo->placa }} - {{ $veiculo->modelo }} {{ $veiculo->marca }} ({{ $veiculo->cliente->nome }})
                </option>
            @endforeach
        </select>
    </div>

    <div class="mb-3">
        <label class="form-label-custom">Checklist de entrada (opcional)</label>
        <select name="checklist_entrada_id" class="form-select">
            <option value="">Sem checklist vinculado</option>
            @foreach ($checklists as $checklist)
                <option value="{{ $checklist->id }}" @selected(old('checklist_entrada_id') == $checklist->id)>
                    #{{ $checklist->id }} · {{ $checklist->data_entrada?->format('d/m/Y') }} · {{ $checklist->veiculo->placa ?? 'veículo '.$checklist->veiculo_id }}
                </option>
            @endforeach
        </select>
    </div>

    <div class="mb-3">
        <label class="form-label-custom">Observações</label>
        <textarea name="observacoes" class="form-control" rows="3" placeholder="Outras observações relevantes">{{ old('observacoes') }}</textarea>
    </div>

    @include('fragments.form-actions', ['actionLabel' => 'Abrir atendimento', 'cancelarUrl' => route('atendimentos.index')])
</form>
@endsection
