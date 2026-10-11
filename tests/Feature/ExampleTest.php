<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
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
}
