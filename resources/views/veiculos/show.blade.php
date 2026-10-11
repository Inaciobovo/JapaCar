@extends('layouts.app')

@section('titulo', $veiculo->placa)

@section('conteudo')
<div class="d-flex align-items-center justify-content-between mb-2">
    <div class="d-flex align-items-center">
        <a href="{{ route('veiculos.index') }}" class="btn btn-sm btn-outline-secondary me-2 no-print">
            <i class="bi bi-arrow-left"></i>
        </a>
        <h1 class="page-title mb-0">
            <span class="text-uppercase">{{ $veiculo->placa }}</span>
        </h1>
    </div>
    <div class="d-flex gap-2 no-print">
        <a href="{{ route('veiculos.edit', $veiculo) }}" class="btn btn-sm btn-outline-secondary">
            <i class="bi bi-pencil me-1"></i> Editar
        </a>
    </div>
</div>
<p class="page-subtitle">{{ $veiculo->modelo }} {{ $veiculo->marca }}</p>

@include('fragments.alerts')

<div class="row">
    <div class="col-12 col-lg-5">
        <div class="card-custom">
            <h6 class="fw-bold mb-1"><i class="bi bi-car-front me-1"></i> Dados do veículo</h6>
            <ul class="detail-list">
                <li>
                    <span class="detail-label">Placa</span>
                    <span class="detail-value fw-bold text-uppercase">{{ $veiculo->placa }}</span>
                </li>
                <li>
                    <span class="detail-label">Veículo</span>
                    <span class="detail-value">{{ $veiculo->modelo }} {{ $veiculo->marca }}</span>
                </li>
                <li>
                    <span class="detail-label">Ano / Cor</span>
                    <span class="detail-value">{{ $veiculo->ano ?? '-' }}/{{ $veiculo->cor ?: '-' }}</span>
                </li>
                <li>
                    <span class="detail-label">Cliente</span>
                    <span class="detail-value">{{ $veiculo->cliente->nome }}</span>
                </li>
            </ul>
            <div class="d-flex flex-column gap-2 mt-3 no-print">
                <a href="{{ route('checklists.create', ['veiculo_id' => $veiculo->id]) }}" class="btn btn-japacar btn-sm">
                    <i class="bi bi-clipboard-check me-1"></i> Novo checklist
                </a>
                <a href="{{ route('atendimentos.create', ['veiculo_id' => $veiculo->id]) }}" class="btn btn-outline-secondary btn-sm">
                    <i class="bi bi-tools me-1"></i> Novo atendimento
                </a>
            </div>
        </div>
    </div>

    <div class="col-12 col-lg-7">
        <div class="card-custom">
            <h6 class="fw-bold mb-3"><i class="bi bi-clipboard-check me-1"></i> Checklists de entrada</h6>
            @forelse ($veiculo->checklistEntradas->sortByDesc('data_entrada') as $checklist)
                <div class="border-bottom pb-3 mb-3">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <div class="fw-semibold">{{ $checklist->data_entrada?->format('d/m/Y H:i') }}</div>
                            <small class="text-muted">
                                {{ $checklist->quilometragem ? number_format($checklist->quilometragem, 0, ',', '.') . ' km' : 'km não informado' }}
                                · {{ $checklist->nivelCombustivelDescricao() ?? '—' }}
                            </small>
                        </div>
                        <div class="text-nowrap">
                            <a href="{{ route('checklists.show', $checklist) }}" class="btn btn-sm btn-outline-secondary" title="Ver">
                                <i class="bi bi-eye"></i>
                            </a>
                            <a href="{{ route('checklists.edit', $checklist) }}" class="btn btn-sm btn-outline-secondary" title="Editar">
                                <i class="bi bi-pencil"></i>
                            </a>
                        </div>
                    </div>
                    @if ($checklist->fotos->isNotEmpty())
                        <div class="photo-grid">
                            @foreach ($checklist->fotos as $foto)
                                <div class="photo-item">
                                    <img src="{{ route('checklists.fotos.arquivo', $foto) }}" alt="Foto do checklist"
                                         data-bs-toggle="modal" data-bs-target="#fotoModal"
                                         data-foto-full="{{ route('checklists.fotos.arquivo', $foto) }}">
                                </div>
                            @endforeach
                        </div>
                    @endif
                </div>
            @empty
                <p class="text-muted mb-0">Nenhum checklist registrado.</p>
            @endforelse
        </div>
    </div>
</div>

@php
    $temFotos = $veiculo->checklistEntradas->contains(fn ($c) => $c->fotos->isNotEmpty());
@endphp
@if ($temFotos)
    <div class="modal fade" id="fotoModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content" style="background:rgba(0,0,0,0.85);">
                <div class="modal-body p-0 position-relative">
                    <img id="fotoAmpliada" src="" alt="Foto ampliada" class="w-100 rounded">
                    <button type="button" class="btn btn-sm position-absolute top-0 end-0 m-2"
                            style="background:rgba(0,0,0,0.6);color:#fff;" data-bs-dismiss="modal">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>
@endif

<div class="card-custom">
    <h6 class="fw-bold mb-3"><i class="bi bi-tools me-1"></i> Atendimentos</h6>
    @forelse ($veiculo->atendimentos->sortByDesc('created_at') as $atendimento)
        <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
            <div>
                <a href="{{ route('atendimentos.show', $atendimento) }}" class="fw-semibold text-decoration-none">
                    Serviço #{{ $atendimento->id }}
                </a>
                <span class="badge badge-status {{ $atendimento->finalizado() ? 'badge-concluido' : 'badge-em-andamento' }}">
                    {{ $atendimento->statusDescricao() }}
                </span>
            </div>
            <a href="{{ route('atendimentos.show', $atendimento) }}" class="btn btn-sm btn-outline-secondary">Abrir</a>
        </div>
    @empty
        <p class="text-muted mb-0">Nenhum atendimento registrado.</p>
    @endforelse
</div>
@endsection
