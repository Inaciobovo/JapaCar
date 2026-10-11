<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('veiculos', function (Blueprint $table) {
            $table->id();
            $table->string('placa')->unique();
            $table->string('modelo');
            $table->string('marca');
            $table->integer('ano')->nullable();
            $table->string('cor')->nullable();
            $table->foreignId('cliente_id')->constrained('clientes')->cascadeOnDelete();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('veiculos');
    }
};
