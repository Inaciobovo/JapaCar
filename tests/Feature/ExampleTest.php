<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Hash;
use Tests\TestCase;

class ExampleTest extends TestCase
{
    use RefreshDatabase;

    public function test_home_redirects_to_atendimentos(): void
    {
        $this->get('/')->assertRedirect(route('atendimentos.index'));
    }

    public function test_login_page_renders(): void
    {
        $this->get('/login')->assertOk()->assertSee('JAPACAR');
    }

    public function test_guests_are_redirected_to_login(): void
    {
        $this->get('/painel')->assertRedirect(route('login'));
    }

    public function test_authenticated_user_can_access_painel(): void
    {
        $user = User::factory()->create();

        $this->actingAs($user)->get('/painel')->assertOk();
    }

    public function test_user_can_change_password(): void
    {
        $user = User::factory()->create(['password' => 'senha-atual-123']);

        $this->actingAs($user)->put('/perfil/senha', [
            'senha_atual' => 'senha-atual-123',
            'senha' => 'nova-senha-123',
            'senha_confirmation' => 'nova-senha-123',
        ])->assertRedirect();

        $this->assertTrue(Hash::check('nova-senha-123', $user->fresh()->password));
    }

    public function test_password_change_requires_correct_current_password(): void
    {
        $user = User::factory()->create(['password' => 'senha-atual-123']);

        $this->actingAs($user)->put('/perfil/senha', [
            'senha_atual' => 'errada',
            'senha' => 'nova-senha-123',
            'senha_confirmation' => 'nova-senha-123',
        ])->assertSessionHasErrors('senha_atual');
    }
}
