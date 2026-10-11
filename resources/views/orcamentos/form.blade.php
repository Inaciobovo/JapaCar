@extends('layouts.app')

@section('titulo', 'Novo Orçamento')

@section('conteudo')
<div class="d-flex align-items-center mb-2">
    <a href="{{ route('atendimentos.show', $atendimento) }}" class="btn btn-sm btn-outline-secondary me-2 no-print">
        <i class="bi bi-arrow-left"></i>
    </a>
    <h1 class="page-title mb-0">Novo Orçamento</h1>
</div>
<p class="page-subtitle">
    {{ $atendimento->veiculo->placa }} - {{ $atendimento->veiculo->modelo }} {{ $atendimento->veiculo->marca }} ({{ $atendimento->veiculo->cliente->nome }})
</p>

@include('fragments.alerts')

<form action="{{ route('orcamentos.store') }}" method="post" class="form-card">
    @csrf
    <input type="hidden" name="atendimento_id" value="{{ $atendimento->id }}">

    <div class="row">
        <div class="col-12 col-md-6 mb-3">
            <label class="form-label-custom">Valor mão de obra (R$)</label>
            <input type="number" step="0.01" min="0" name="valor_mao_de_obra" class="form-control"
                   value="{{ old('valor_mao_de_obra', '0.00') }}" required placeholder="0,00">
        </div>
        <div class="col-12 col-md-6 mb-3">
            <label class="form-label-custom">Status</label>
            <input type="text" class="form-control" value="Pendente" disabled>
            <div class="form-text">Novo orçamento inicia como <strong>Pendente</strong>.</div>
        </div>
    </div>

    <div class="mb-3">
        <label class="form-label-custom">Observações</label>
        <textarea name="observacoes" class="form-control" rows="3" placeholder="Observações do orçamento">{{ old('observacoes') }}</textarea>
    </div>

    <div class="form-text mb-2">As peças/itens são adicionados depois, na tela do orçamento.</div>

    @include('fragments.form-actions', ['actionLabel' => 'Salvar orçamento', 'cancelarUrl' => route('atendimentos.show', $atendimento)])
</form>
@endsection
