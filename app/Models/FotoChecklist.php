<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Fillable(['checklist_entrada_id', 'caminho_arquivo', 'descricao'])]
class FotoChecklist extends Model
{
    public function checklist(): BelongsTo
    {
        return $this->belongsTo(ChecklistEntrada::class, 'checklist_entrada_id');
    }
}
