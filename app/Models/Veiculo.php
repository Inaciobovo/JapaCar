<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

#[Fillable(['placa', 'modelo', 'marca', 'ano', 'cor', 'cliente_id'])]
class Veiculo extends Model
{
    public function cliente(): BelongsTo
    {
        return $this->belongsTo(Cliente::class);
    }

    public function checklistEntradas(): HasMany
    {
        return $this->hasMany(ChecklistEntrada::class);
    }

    public function atendimentos(): HasMany
    {
        return $this->hasMany(Atendimento::class);
    }

    protected function casts(): array
    {
        return [
            'ano' => 'integer',
        ];
    }
}
