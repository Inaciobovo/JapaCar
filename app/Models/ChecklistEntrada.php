<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

#[Fillable([
    'veiculo_id',
    'data_entrada',
    'quilometragem',
    'nivel_combustivel',
    'condicoes_lataria',
    'observacoes_gerais',
    'responsavel',
])]
class ChecklistEntrada extends Model
{
    public function veiculo(): BelongsTo
    {
        return $this->belongsTo(Veiculo::class);
    }

    public function fotos(): HasMany
    {
        return $this->hasMany(FotoChecklist::class);
    }

    public function nivelCombustivelDescricao(): ?string
    {
        return config('japacar.nivel_combustivel')[$this->nivel_combustivel] ?? $this->nivel_combustivel;
    }

    protected function casts(): array
    {
        return [
            'data_entrada' => 'datetime',
            'quilometragem' => 'integer',
        ];
    }
}
