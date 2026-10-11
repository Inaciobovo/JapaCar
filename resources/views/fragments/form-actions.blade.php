<div class="form-actions">
    <button type="submit" class="btn btn-japacar">
        <i class="bi bi-check-lg me-1"></i> {{ $actionLabel ?? 'Salvar' }}
    </button>
    <a href="{{ $cancelarUrl ?? '/' }}" class="btn btn-outline-secondary">
        <i class="bi bi-x-lg me-1"></i> Cancelar
    </a>
</div>
