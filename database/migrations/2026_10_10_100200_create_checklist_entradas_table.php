<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('checklist_entradas', function (Blueprint $table) {
            $table->id();
            $table->foreignId('veiculo_id')->constrained('veiculos')->cascadeOnDelete();
            $table->timestamp('data_entrada')->useCurrent();
            $table->integer('quilometragem')->nullable();
            $table->string('nivel_combustivel')->nullable();
            $table->text('condicoes_lataria')->nullable();
            $table->text('observacoes_gerais')->nullable();
            $table->string('responsavel')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('checklist_entradas');
    }
};
