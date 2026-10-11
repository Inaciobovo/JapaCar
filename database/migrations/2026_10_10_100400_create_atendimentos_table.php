<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('atendimentos', function (Blueprint $table) {
            $table->id();
            $table->foreignId('veiculo_id')->constrained('veiculos')->cascadeOnDelete();
            $table->foreignId('checklist_entrada_id')->nullable()->constrained('checklist_entradas')->nullOnDelete();
            $table->string('status')->default('EM_ANDAMENTO');
            $table->text('observacoes')->nullable();
            $table->timestamp('data_finalizacao')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('atendimentos');
    }
};
