<!DOCTYPE html>
<html lang="pt-BR">
@include('fragments.head')
<body class="{{ $deviceClass }}">
@include('fragments.sidebar')

<div class="d-flex flex-column flex-lg-row w-100">
    <div class="flex-grow-1 d-flex flex-column" style="min-height:100vh;">
        @include('fragments.header')

        <main class="app-main flex-grow-1">
            @yield('conteudo')
        </main>

        <footer class="text-center text-muted small py-3 no-print">
            JAPACAR · Sistema de gestão para oficina mecânica
        </footer>
    </div>
</div>

@include('fragments.bottom-nav')
@include('fragments.scripts')
@stack('scripts')
</body>
</html>
