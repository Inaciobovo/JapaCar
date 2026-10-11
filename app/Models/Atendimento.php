<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

#[Fillable(['veiculo_id', 'checklist_entrada_id', 'status', 'observacoes', 'data_finalizacao'])]
class Atendimento extends Model
{
    public function veiculo(): BelongsTo
    {
        return $this->belongsTo(Veiculo::class);
    }

    public function checklistEntrada(): BelongsTo
    {
        return $this->belongsTo(ChecklistEntrada::class);
    }

    public function orcamentos(): HasMany
    {
        return $this->hasMany(Orcamento::class)->latest();
    }

    public function statusDescricao(): string
    {
        return config('japacar.status_atendimento')[$this->status] ?? $this->status;
    }

    public function finalizado(): bool
    {
        return $this->status === 'FINALIZADO';
    }

    protected function casts(): array
    {
        return [
            'data_finalizacao' => 'datetime',
        ];
    }
}
