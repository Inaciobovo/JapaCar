<?php

namespace App\Support;

use Illuminate\Http\Request;

class Japacar
{
    public static function isMobile(?Request $request = null): bool
    {
        $userAgent = ($request ?? request())->userAgent() ?? '';

        return (bool) preg_match('/Mobile|Android|iPhone|iPad|iPod|Opera Mini|IEMobile|WPDesktop|webOS|BlackBerry|Windows Phone/i', $userAgent);
    }

    public static function deviceClass(): string
    {
        return self::isMobile() ? 'device-mobile' : 'device-desktop';
    }
}
