<?php

namespace Tests\Feature;

use App\Run;
use App\WatchedRun;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\DB;
use Tests\TestCase;

/**
 * The homepage's most-watched section, around #107's reset.
 *
 * Three things are being pinned. That a retired watch does not count - the
 * reset is the `old` column doing the work, with nothing deleted. That the
 * cutoff is the epic rather than everything, so a watch cast while the
 * backfilled events were already on the site survives. And that an empty
 * result renders *nothing*: `$runs` is an Eloquent Collection, so a bare
 * `@if($runs)` is an object test that passes on an empty collection and leaves
 * a bald table header on the page.
 */
class HomepageWatchCountsTest extends TestCase
{
    use RefreshDatabase;

    /** Midnight UTC on the day epic #31 was opened; see the reset migration. */
    private const EPIC_STARTED = '2026-08-23 00:00:00';

    private function watch(Run $run, string $ip, ?string $at = null, bool $old = false): int
    {
        $id = DB::table('watched_runs')->insertGetId([
            'run_id' => $run->id,
            'ip' => $ip,
            'created_at' => $at,
            'updated_at' => $at,
        ]);

        if ($old) {
            DB::table('watched_runs')->where('id', $id)->update(['old' => 1]);
        }

        return $id;
    }

    /**
     * The reset itself - the same method the migration calls, not a copy of it.
     *
     * A migration body cannot be exercised directly: by the time a test has
     * rows to reset, its migrations have run against an empty table. Calling
     * the shared method is what keeps these assertions about the real thing.
     */
    private function runTheReset(): int
    {
        return WatchedRun::retireWatchesBefore(self::EPIC_STARTED);
    }

    public function test_a_watch_from_before_the_epic_is_retired(): void
    {
        $run = Run::factory()->create();
        $this->watch($run, '10.0.0.1', '2026-08-22 23:59:59');

        $this->runTheReset();

        $this->assertSame([], WatchedRun::getTopWatchedRunIds());
        // Retired, not deleted.
        $this->assertSame(1, DB::table('watched_runs')->count());
    }

    public function test_a_watch_from_during_the_backfill_survives(): void
    {
        $run = Run::factory()->create();
        $this->watch($run, '10.0.0.1', '2026-08-23 00:00:00');

        $this->runTheReset();

        // This is the whole point of the cutoff: it was cast against a site
        // that already had backfilled events on it, so it is real signal.
        $this->assertSame([$run->id], WatchedRun::getTopWatchedRunIds());
    }

    public function test_a_watch_with_no_timestamp_is_treated_as_pre_epic(): void
    {
        $run = Run::factory()->create();
        $this->watch($run, '10.0.0.1', null);

        $this->runTheReset();

        $this->assertSame([], WatchedRun::getTopWatchedRunIds());
    }

    public function test_the_reset_is_a_no_op_the_second_time(): void
    {
        $run = Run::factory()->create();
        $this->watch($run, '10.0.0.1', '2026-08-22 12:00:00');
        $this->watch($run, '10.0.0.2', '2026-09-01 12:00:00');

        $this->assertSame(1, $this->runTheReset(), 'first pass retires the pre-epic row');
        $this->assertSame(0, $this->runTheReset(), 'second pass has nothing left to do');

        $this->assertSame(1, DB::table('watched_runs')->where('old', 1)->count());
        $this->assertSame([$run->id], WatchedRun::getTopWatchedRunIds());
    }

    public function test_a_watched_run_still_reaches_the_homepage(): void
    {
        $run = Run::factory()->create();
        $this->watch($run, '10.0.0.1', '2026-09-01 12:00:00');

        $this->get('/')->assertOk()->assertSee('id="mainTable"', false);
    }

    public function test_the_table_is_absent_entirely_when_nothing_counts(): void
    {
        $run = Run::factory()->create();
        $this->watch($run, '10.0.0.1', '2026-08-01 12:00:00');
        $this->runTheReset();

        $response = $this->get('/')->assertOk();

        // Not merely "no rows": no table at all. A truthiness guard on the
        // collection would leave the header behind and still pass a row check.
        $response->assertDontSee('id="mainTable"', false);
        $response->assertDontSee('<th>Game</th>', false);

        // The page still renders - this is an empty state, not an error.
        $response->assertSee('Welcome to ESA VODs', false);
    }
}
