<?php

use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        api: __DIR__.'/../routes/api.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        // Carried over from the Laravel 5.7 Http\Kernel. The framework default
        // sends an already-authenticated visitor to /dashboard when a route with
        // that URI exists, which this app has; the 5.7 behaviour was always "/".
        $middleware->alias([
            'guest' => \App\Http\Middleware\RedirectIfAuthenticated::class,
        ]);

        // TLS terminates at Cloudflare; the origin only ever sees the tunnel.
        // Without this, Laravel builds absolute URLs from the request it
        // actually receives (http, tunnel IP) instead of X-Forwarded-*.
        $middleware->trustProxies(at: '*');
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        //
    })->create();
