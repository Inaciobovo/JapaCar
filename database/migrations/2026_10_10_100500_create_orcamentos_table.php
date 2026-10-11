<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('orcamentos', function (Blueprint $table) {
            $table->id();
            $table->foreignId('atendimento_id')->constrained('atendimentos')->cascadeOnDelete();
            $table->decimal('valor_mao_de_obra', 10, 2)->default(0);
            $table->decimal('valor_pecas', 10, 2)->default(0);
            $table->decimal('valor_total', 10, 2)->default(0);
            $table->string('status')->default('PENDENTE');
            $table->string('status_pagamento')->default('PENDENTE');
            $table->string('forma_pagamento')->nullable();
            $table->date('data_pagamento')->nullable();
            $table->decimal('valor_pago', 10, 2)->default(0);
            $table->string('observacoes')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('orcamentos');
    }
};
