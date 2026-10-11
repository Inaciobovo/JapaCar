<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

#[Fillable(['nome', 'cpf', 'telefone', 'email', 'endereco', 'ativo'])]
class Cliente extends Model
{
    public function veiculos(): HasMany
    {
        return $this->hasMany(Veiculo::class);
    }

    protected function casts(): array
    {
        return [
            'ativo' => 'boolean',
        ];
    }
}
