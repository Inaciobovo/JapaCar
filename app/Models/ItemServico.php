<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Fillable(['orcamento_id', 'descricao', 'quantidade', 'valor_unitario'])]
class ItemServico extends Model
{
    public function orcamento(): BelongsTo
    {
        return $this->belongsTo(Orcamento::class);
    }

    public function getSubtotalAttribute(): float
    {
        $quantidade = $this->quantidade ?? 1;

        return (float) $this->valor_unitario * $quantidade;
    }

    protected function casts(): array
    {
        return [
            'quantidade' => 'integer',
            'valor_unitario' => 'decimal:2',
        ];
    }
}
