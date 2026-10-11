@extends('layouts.app')

@section('titulo', 'Checklist #'.$checklist->id)

@section('conteudo')
<div class="d-flex align-items-center justify-content-between mb-2">
    <div class="d-flex align-items-center">
        <a href="{{ route('checklists.index') }}" class="btn btn-sm btn-outline-secondary me-2 no-print">
            <i class="bi bi-arrow-left"></i>
        </a>
        <h1 class="page-title mb-0">Checklist #{{ $checklist->id }}</h1>
    </div>
    <a href="{{ route('checklists.edit', $checklist) }}" class="btn btn-sm btn-outline-secondary no-print">
        <i class="bi bi-pencil me-1"></i> Editar
    </a>
</div>
<p class="page-subtitle">Registro das condições do veículo na entrada</p>

@include('fragments.alerts')

<div class="row">
    <div class="col-12 col-lg-7">
        <div class="card-custom">
            <h6 class="fw-bold mb-3"><i class="bi bi-clipboard-check me-1"></i> Dados do checklist</h6>
            <ul class="detail-list">
                <li>
                    <span class="detail-label">Data de entrada</span>
                    <span class="detail-value">{{ $checklist->data_entrada?->format('d/m/Y H:i') }}</span>
                </li>
                <li>
                    <span class="detail-label">Responsável</span>
                    <span class="detail-value">{{ $checklist->responsavel }}</span>
                </li>
                <li>
                    <span class="detail-label">Quilometragem</span>
                    <span class="detail-value">{{ $checklist->quilometragem !== null ? $checklist->quilometragem . ' km' : '-' }}</span>
                </li>
                <li>
                    <span class="detail-label">Nível de combustível</span>
                    <span class="detail-value">{{ $checklist->nivel_combustivel ? $checklist->nivelCombustivelDescricao() : '-' }}</span>
                </li>
            </ul>

            <h6 class="fw-bold mt-4 mb-2">Condições da lataria</h6>
            <p class="mb-0">{{ $checklist->condicoes_lataria ?: '— Sem observações —' }}</p>

            <h6 class="fw-bold mt-3 mb-2">Observações gerais</h6>
            <p class="mb-0">{{ $checklist->observacoes_gerais ?: '— Sem observações —' }}</p>
        </div>
    </div>

    <div class="col-12 col-lg-5">
        <div class="card-custom">
            <h6 class="fw-bold mb-1"><i class="bi bi-car-front me-1"></i> Veículo</h6>
            <ul class="detail-list">
                <li>
                    <span class="detail-label">Placa</span>
                    <span class="detail-value fw-bold text-uppercase">{{ $checklist->veiculo->placa }}</span>
                </li>
                <li>
                    <span class="detail-label">Veículo</span>
                    <span class="detail-value">{{ $checklist->veiculo->modelo }} {{ $checklist->veiculo->marca }}</span>
                </li>
                <li>
                    <span class="detail-label">Ano / Cor</span>
                    <span class="detail-value">{{ $checklist->veiculo->ano ?? '-' }}/{{ $checklist->veiculo->cor ?: '-' }}</span>
                </li>
                <li>
                    <span class="detail-label">Cliente</span>
                    <span class="detail-value">{{ $checklist->veiculo->cliente->nome }}</span>
                </li>
            </ul>
        </div>
    </div>
</div>

@if ($checklist->fotos->isNotEmpty())
    <div class="card-custom">
        <h6 class="fw-bold mb-3"><i class="bi bi-images me-1"></i> Registro fotográfico ({{ $checklist->fotos->count() }})</h6>
        <div class="photo-grid">
            @foreach ($checklist->fotos as $foto)
                <div class="photo-item">
                    <img src="{{ route('checklists.fotos.arquivo', $foto) }}" alt="Foto do checklist"
                         data-bs-toggle="modal" data-bs-target="#fotoModal"
                         data-foto-full="{{ route('checklists.fotos.arquivo', $foto) }}">
                </div>
            @endforeach
        </div>
    </div>
@else
    <div class="card-custom text-center py-4">
        <i class="bi bi-images text-muted display-4"></i>
        <p class="text-muted mt-2 mb-0">Nenhuma foto registrada neste checklist.</p>
    </div>
@endif

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
@endsection

@push('scripts')
<script>
    document.addEventListener('click', function (e) {
        const img = e.target.closest('img[data-foto-full]');
        if (img) {
            document.getElementById('fotoAmpliada').src = img.getAttribute('data-foto-full');
        }
    });
</script>
@endpush
