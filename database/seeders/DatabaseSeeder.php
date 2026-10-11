<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    public function run(): void
    {
        User::firstOrCreate(
            ['login' => env('ADMIN_LOGIN', 'admin')],
            [
                'nome' => 'Administrador',
                'password' => env('ADMIN_PASSWORD', 'japacar123'),
                'perfil' => 'ADMIN',
                'ativo' => true,
            ],
        );
    }
}
