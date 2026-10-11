<?php

namespace App\Http\Controllers;

use App\Models\ChecklistEntrada;
use App\Models\FotoChecklist;
use App\Models\Veiculo;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Validation\Rule;

class ChecklistController extends Controller
{
    private const REGRAS_FOTO = ['image', 'mimes:jpg,jpeg,png,webp', 'max:5120'];

    public function index()
    {
        $checklists = ChecklistEntrada::with('veiculo.cliente')
            ->latest('data_entrada')
            ->paginate(20);

        return view('checklists.index', compact('checklists'));
    }

    public function create(Request $request)
    {
        return view('checklists.form', [
            'checklist' => new ChecklistEntrada([
                'veiculo_id' => $request->integer('veiculo_id') ?: null,
                'data_entrada' => now(),
            ]),
            'veiculos' => Veiculo::with('cliente')->orderBy('placa')->get(),
        ]);
    }

    public function store(Request $request)
    {
        $checklist = ChecklistEntrada::create($this->validados($request));
        $this->salvarFotos($request, $checklist);

        return redirect()
            ->route('veiculos.show', $checklist->veiculo_id)
            ->with('status', 'Checklist registrado.');
    }

    public function edit(ChecklistEntrada $checklist)
    {
        return view('checklists.form', [
            'checklist' => $checklist->load('fotos'),
            'veiculos' => Veiculo::with('cliente')->orderBy('placa')->get(),
        ]);
    }

    public function update(Request $request, ChecklistEntrada $checklist)
    {
        $checklist->update($this->validados($request));
        $this->salvarFotos($request, $checklist);

        return redirect()
            ->route('veiculos.show', $checklist->veiculo_id)
            ->with('status', 'Checklist atualizado.');
    }

    public function addFoto(Request $request, ChecklistEntrada $checklist)
    {
        $request->validate([
            'fotos' => ['required', 'array'],
            'fotos.*' => self::REGRAS_FOTO,
        ]);

        $this->salvarFotos($request, $checklist);

        return back()->with('status', 'Fotos adicionadas.');
    }

    public function removeFoto(FotoChecklist $foto)
    {
        Storage::disk('local')->delete($foto->caminho_arquivo);
        $foto->delete();

        return back()->with('status', 'Foto removida.');
    }

    public function serveFoto(FotoChecklist $foto)
    {
        abort_unless(Storage::disk('local')->exists($foto->caminho_arquivo), 404);

        return response()->file(Storage::disk('local')->path($foto->caminho_arquivo));
    }

    private function salvarFotos(Request $request, ChecklistEntrada $checklist): void
    {
        $request->validate([
            'fotos' => ['nullable', 'array'],
            'fotos.*' => self::REGRAS_FOTO,
        ]);

        foreach ($request->file('fotos') ?? [] as $arquivo) {
            $caminho = $arquivo->store('uploads/checklists', 'local');

            $checklist->fotos()->create([
                'caminho_arquivo' => $caminho,
                'descricao' => null,
            ]);
        }
    }

    /**
     * @return array<string, mixed>
     */
    private function validados(Request $request): array
    {
        return $request->validate([
            'veiculo_id' => ['required', 'integer', 'exists:veiculos,id'],
            'data_entrada' => ['required', 'date'],
            'quilometragem' => ['nullable', 'integer', 'min:0'],
            'nivel_combustivel' => ['nullable', Rule::in(array_keys(config('japacar.nivel_combustivel')))],
            'condicoes_lataria' => ['nullable', 'string', 'max:2000'],
            'observacoes_gerais' => ['nullable', 'string', 'max:2000'],
            'responsavel' => ['nullable', 'string', 'max:255'],
        ]);
    }
}
