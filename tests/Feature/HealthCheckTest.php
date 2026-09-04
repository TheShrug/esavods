<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

/**
 * /up, registered by bootstrap/app.php's `health:` argument.
 *
 * It is the Dockerfile's HEALTHCHECK and the first of the two paths deploy.yml
 * curls from the public internet after a release, so it is load-bearing well
 * outside the browser: if it stops answering 200 the container never reports
 * healthy and Coolify fails the deploy.
 */
class HealthCheckTest extends TestCase
{
    use RefreshDatabase;

    public function test_the_health_endpoint_returns_200(): void
    {
        $this->get('/up')->assertOk();
    }
}
