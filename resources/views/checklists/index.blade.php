@extends('layouts.app')

@section('titulo', 'Checklists de Entrada')

@section('conteudo')
<div class="d-flex align-items-center justify-content-between mb-2">
    <h1 class="page-title">Checklists de Entrada</h1>
    <a href="{{ route('checklists.create') }}" class="btn btn-sm btn-japacar">
        <i class="bi bi-plus-lg me-1"></i> Novo
    </a>
</div>
<p class="page-subtitle">Histórico de checklists dos veículos</p>

@include('fragments.alerts')

<div class="filter-bar">
    <div style="flex:1 1 140px;">
        <label class="form-label-custom">Placa</label>
        <input type="text" id="filtro-placa" class="form-control form-control-sm" placeholder="Buscar pela placa...">
    </div>
    <div style="flex:1 1 130px;">
        <label class="form-label-custom">De</label>
        <input type="date" id="filtro-inicio" class="form-control form-control-sm">
    </div>
    <div style="flex:1 1 130px;">
        <label class="form-label-custom">Até</label>
        <input type="date" id="filtro-fim" class="form-control form-control-sm">
    </div>
    <div style="flex:1 1 150px;">
        <label class="form-label-custom">Responsável</label>
        <input type="text" id="filtro-responsavel" class="form-control form-control-sm">
    </div>
</div>

@if ($checklists->isNotEmpty())
    <div class="table-responsive d-none d-lg-block">
        <table class="table table-hover" id="tabela-checklists">
            <thead>
            <tr>
                <th>Data entrada</th>
                <th>Veículo</th>
                <th>Placa</th>
                <th>Km</th>
                <th>Responsável</th>
                <th class="text-end">Ações</th>
            </tr>
            </thead>
            <tbody>
            @foreach ($checklists as $checklist)
                <tr data-placa="{{ $checklist->veiculo->placa }}"
                    data-responsavel="{{ $checklist->responsavel }}"
                    data-data="{{ $checklist->data_entrada?->format('Y-m-d') }}">
                    <td>{{ $checklist->data_entrada?->format('d/m/Y H:i') }}</td>
                    <td>{{ $checklist->veiculo->modelo }} {{ $checklist->veiculo->marca }}</td>
                    <td><span class="text-uppercase fw-semibold">{{ $checklist->veiculo->placa }}</span></td>
                    <td>{{ $checklist->quilometragem ?? '-' }}</td>
                    <td>{{ $checklist->responsavel }}</td>
                    <td class="text-end text-nowrap">
                        <a href="{{ route('checklists.show', $checklist) }}" class="btn btn-sm btn-outline-secondary" title="Ver">
                            <i class="bi bi-eye"></i>
                        </a>
                        <a href="{{ route('checklists.edit', $checklist) }}" class="btn btn-sm btn-outline-secondary" title="Editar">
                            <i class="bi bi-pencil"></i>
                        </a>
                    </td>
                </tr>
            @endforeach
            </tbody>
        </table>
    </div>
@endif

@if ($checklists->isNotEmpty())
    <div class="list-cards d-lg-none" id="cards-checklists">
        @foreach ($checklists as $checklist)
            <div class="list-card" data-placa="{{ $checklist->veiculo->placa }}"
                 data-responsavel="{{ $checklist->responsavel }}"
                 data-data="{{ $checklist->data_entrada?->format('Y-m-d') }}">
                <div class="lc-top">
                    <div class="lc-title">
                        <span class="text-uppercase">{{ $checklist->veiculo->placa }}</span>
                        <small>{{ $checklist->veiculo->modelo }} {{ $checklist->veiculo->marca }}</small>
                    </div>
                    <i class="bi bi-clipboard-check fs-4" style="color:#e94560;"></i>
                </div>
                <div class="lc-meta">
                    <span>Entrada</span>
                    <strong>{{ $checklist->data_entrada?->format('d/m/Y H:i') }}</strong>
                    <span>Km</span>
                    <strong>{{ $checklist->quilometragem ?? '-' }}</strong>
                    <span>Responsável</span>
                    <strong>{{ $checklist->responsavel }}</strong>
                </div>
                <div class="lc-actions">
                    <a href="{{ route('checklists.show', $checklist) }}" class="btn btn-sm btn-outline-secondary">
                        <i class="bi bi-eye me-1"></i> Ver
                    </a>
                    <a href="{{ route('checklists.edit', $checklist) }}" class="btn btn-sm btn-outline-secondary">
                        <i class="bi bi-pencil me-1"></i> Editar
                    </a>
                </div>
            </div>
        @endforeach
    </div>
@endif

@if ($checklists->isEmpty())
    <div class="card-custom text-center py-5">
        <i class="bi bi-clipboard-check display-4 text-muted"></i>
        <p class="text-muted mt-3 mb-0">Nenhum checklist registrado ainda.</p>
        <a href="{{ route('checklists.create') }}" class="btn btn-sm mt-3 btn-japacar">Iniciar checklist</a>
    </div>
@endif

@if ($checklists->hasPages())
    <div class="mt-3">{{ $checklists->links('pagination::bootstrap-5') }}</div>
@endif
@endsection

@push('scripts')
<script>
    (function () {
        const inputPlaca = document.getElementById('filtro-placa');
        const inputInicio = document.getElementById('filtro-inicio');
        const inputFim = document.getElementById('filtro-fim');
        const inputResp = document.getElementById('filtro-responsavel');
        if (!inputPlaca || !inputInicio || !inputFim || !inputResp) return;

        function filtrar() {
            const placa = (inputPlaca.value || '').toUpperCase().trim();
            const inicio = inputInicio.value;
            const fim = inputFim.value;
            const resp = (inputResp.value || '').toLowerCase().trim();

            document.querySelectorAll('#tabela-checklists tbody tr, #cards-checklists .list-card').forEach(function (el) {
                const elPlaca = (el.getAttribute('data-placa') || '').toUpperCase();
                const elData = el.getAttribute('data-data') || '';
                const elResp = (el.getAttribute('data-responsavel') || '').toLowerCase();

                let visivel = true;
                if (placa && elPlaca.indexOf(placa) === -1) visivel = false;
                if (visivel && inicio && elData < inicio) visivel = false;
                if (visivel && fim && elData > fim) visivel = false;
                if (visivel && resp && elResp.indexOf(resp) === -1) visivel = false;

                el.style.display = visivel ? '' : 'none';
            });
        }

        inputPlaca.addEventListener('input', filtrar);
        inputInicio.addEventListener('change', filtrar);
        inputFim.addEventListener('change', filtrar);
        inputResp.addEventListener('input', filtrar);
    })();
</script>
@endpush
