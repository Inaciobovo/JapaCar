<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

#[Fillable([
    'atendimento_id',
    'valor_mao_de_obra',
    'valor_pecas',
    'valor_total',
    'status',
    'status_pagamento',
    'forma_pagamento',
    'data_pagamento',
    'valor_pago',
    'observacoes',
])]
class Orcamento extends Model
{
    public function atendimento(): BelongsTo
    {
        return $this->belongsTo(Atendimento::class);
    }

    public function itens(): HasMany
    {
        return $this->hasMany(ItemServico::class)->orderBy('id');
    }

    public function recalcularTotais(): void
    {
        $totalPecas = $this->itens->sum(fn (ItemServico $item) => $item->subtotal);
        $this->valor_pecas = $totalPecas;
        $this->valor_total = $totalPecas + (float) $this->valor_mao_de_obra;
    }

    public function valorRestante(): float
    {
        return max((float) $this->valor_total - (float) $this->valor_pago, 0);
    }

    public function statusDescricao(): string
    {
        return config('japacar.status_orcamento')[$this->status] ?? $this->status;
    }

    public function statusPagamentoDescricao(): string
    {
        return config('japacar.status_pagamento')[$this->status_pagamento] ?? $this->status_pagamento;
    }

    public function formaPagamentoDescricao(): ?string
    {
        return config('japacar.forma_pagamento')[$this->forma_pagamento] ?? $this->forma_pagamento;
    }

    protected function casts(): array
    {
        return [
            'valor_mao_de_obra' => 'decimal:2',
            'valor_pecas' => 'decimal:2',
            'valor_total' => 'decimal:2',
            'valor_pago' => 'decimal:2',
            'data_pagamento' => 'date',
        ];
    }
}
