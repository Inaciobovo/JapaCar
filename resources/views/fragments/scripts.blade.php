@php
    $jsVersion = @filemtime(public_path('js/app.js')) ?: '1';
@endphp
<script src="{{ asset('vendor/bootstrap/js/bootstrap.bundle.min.js') }}"></script>
<script src="{{ asset('js/app.js') }}?v={{ $jsVersion }}"></script>
