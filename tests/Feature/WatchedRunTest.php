<?php

namespace Tests\Feature;

use App\Run;
use App\WatchedRun;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

/**
 * POST /run/{id} - the site's only write endpoint.
 *
 * The player fires it when a VOD is opened, and the homepage table is built
 * from what it records. It is unauthenticated and takes no body, so the only
 * things worth pinning are that it stores a row and that it does not store the
 * same viewer twice.
 */
class WatchedRunTest extends TestCase
{
    use RefreshDatabase;

    public function test_it_records_a_watch(): void
    {
        $run = Run::factory()->create();

        $response = $this->post('/run/'.$run->id);

        $response->assertOk();
        $response->assertExactJson(['success' => true]);

        $this->assertDatabaseHas('watched_runs', [
            'run_id' => $run->id,
            'ip' => '127.0.0.1',
        ]);
    }

    /**
     * firstOrCreate() on (run_id, ip), so a viewer who reopens the same VOD
     * does not count twice. There is no unique index behind it - this is the
     * only thing enforcing it.
     */
    public function test_a_second_watch_from_the_same_ip_does_not_add_a_row(): void
    {
        $run = Run::factory()->create();

        $this->post('/run/'.$run->id)->assertOk();
        $this->post('/run/'.$run->id)->assertOk();

        $this->assertSame(1, WatchedRun::where('run_id', $run->id)->count());
    }

    /**
     * A watch is what puts a run on the homepage, so this is the seam between
     * the write endpoint and the only page that reads it.
     */
    public function test_a_watched_run_reaches_the_home_page(): void
    {
        $run = Run::factory()->create();

        $this->post('/run/'.$run->id)->assertOk();

        $this->get('/')->assertOk()->assertSee('data-id="'.$run->id.'"', false);
    }
}
