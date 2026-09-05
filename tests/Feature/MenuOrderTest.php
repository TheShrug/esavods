<?php

namespace Tests\Feature;

use App\Event;
use App\Run;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Cache;
use Tests\TestCase;

/**
 * The Events dropdown, which the shared layout renders on every page.
 *
 * The assertions read the rendered markup rather than model state, because the
 * order is the whole feature and only the markup shows it. They read the
 * dropdown REGION rather than the whole page: the event index renders the same
 * slugs in a table, in a different order, and a page-wide match would then
 * assert on whichever happened to come first in the HTML.
 */
class MenuOrderTest extends TestCase
{
    use RefreshDatabase;

    /**
     * An event and the dates of its runs. No dates at all means an event that
     * exists but has never had a schedule imported.
     *
     * @param  list<string>  $runDates
     */
    private function event(string $name, string $slug, array $runDates): Event
    {
        $event = Event::factory()->create(['name' => $name, 'slug' => $slug]);

        foreach ($runDates as $runDate) {
            Run::factory()->create(['event_id' => $event->id, 'run_date' => $runDate]);
        }

        return $event;
    }

    /**
     * The event slugs the dropdown links to, in the order it renders them.
     *
     * @return list<string>
     */
    private function dropdownSlugs(string $html): array
    {
        preg_match_all('#/event/([a-z0-9-]+)"#', $this->dropdown($html), $matches);

        return $matches[1];
    }

    /**
     * The events dropdown alone. It starts at its own container class and ends
     * where the platforms dropdown begins.
     */
    private function dropdown(string $html): string
    {
        $start = strpos($html, 'dropdown-menu double');
        $this->assertNotFalse($start, 'the layout rendered no events dropdown');

        $end = strpos($html, 'dropdown-menu triple', $start);
        $this->assertNotFalse($end, 'the layout rendered no platforms dropdown to stop at');

        return substr($html, $start, $end - $start);
    }

    /**
     * The fault in #98, in miniature: an event created LAST but aired first has
     * to sink, and one created first but aired last has to rise, so insertion
     * order cannot pass this by accident.
     */
    public function test_the_dropdown_reads_newest_to_oldest(): void
    {
        $this->event('ESA 2023 Winter', 'esa-2023-winter', ['2023-02-11 10:00:00']);
        $this->event('ESA 2026 Winter', 'esa-2026-winter', ['2026-02-13 10:00:00']);
        $this->event('ESA 2012', 'esa-2012', ['2012-08-16 15:00:00']);
        $this->event('ESA 2023 Summer', 'esa-2023-summer', ['2023-07-15 10:00:00']);

        $slugs = $this->dropdownSlugs($this->get('/')->getContent());

        $this->assertSame([
            'esa-2026-winter',
            // Summer above Winter of the same year, which is the ordering a
            // `year` column cannot express however carefully it is filled in.
            'esa-2023-summer',
            'esa-2023-winter',
            'esa-2012',
        ], $slugs);
    }

    /**
     * MIN(run_date), not MAX and not whichever run comes first in the table: an
     * event is placed by when it started.
     */
    public function test_an_event_is_placed_by_its_first_run(): void
    {
        $this->event('ESA 2024 Summer', 'esa-2024-summer', [
            '2024-07-20 18:00:00',
            '2024-07-13 10:00:00',
            '2024-07-16 12:00:00',
        ]);
        $this->event('ESA 2024 Winter', 'esa-2024-winter', ['2024-02-10 10:00:00']);
        // Starts before ESA 2024 Summer and ends after it. Ordered on its last
        // run it would outrank Summer; on its first it does not.
        $this->event('ESA 2024 Spring', 'esa-2024-spring', [
            '2024-05-01 10:00:00',
            '2024-08-01 10:00:00',
        ]);

        $this->assertSame(
            ['esa-2024-summer', 'esa-2024-spring', 'esa-2024-winter'],
            $this->dropdownSlugs($this->get('/')->getContent())
        );
    }

    /**
     * An event with nothing dated has no place in a chronology, so it goes to
     * the bottom - not the top, which is where Postgres puts it by default,
     * NULLs sorting FIRST under DESC.
     */
    public function test_an_event_with_no_dated_runs_sorts_last(): void
    {
        $this->event('ESA 2012', 'esa-2012', ['2012-08-16 15:00:00']);
        $this->event('ESA Unscheduled', 'esa-unscheduled', []);
        $this->event('ESA 2026 Winter', 'esa-2026-winter', ['2026-02-13 10:00:00']);
        // Runs, but none of them dated - the other way an event ends up with no
        // date, and the one a half-imported CSV produces.
        $dateless = Event::factory()->create(['name' => 'ESA Dateless', 'slug' => 'esa-dateless']);
        Run::factory()->create(['event_id' => $dateless->id, 'run_date' => null]);

        $this->assertSame([
            'esa-2026-winter',
            'esa-2012',
            // Both undated, ordered by name so the tail is at least stable.
            'esa-dateless',
            'esa-unscheduled',
        ], $this->dropdownSlugs($this->get('/')->getContent()));
    }

    /**
     * The grouping exists only to draw separators - $key is never printed - so
     * what is worth pinning is that they land between years, one <hr> per
     * group. Undated events are their own group at the end.
     */
    public function test_a_separator_falls_between_years(): void
    {
        $this->event('ESA 2026 Winter', 'esa-2026-winter', ['2026-02-13 10:00:00']);
        $this->event('ESA 2023 Summer', 'esa-2023-summer', ['2023-07-15 10:00:00']);
        $this->event('ESA 2023 Winter', 'esa-2023-winter', ['2023-02-11 10:00:00']);
        $this->event('ESA Unscheduled', 'esa-unscheduled', []);

        $dropdown = $this->dropdown($this->get('/')->getContent());

        $this->assertSame(3, substr_count($dropdown, '<hr>'), 'expected one separator per year group');
    }

    /**
     * The layout calls ->chunk(2) on every group. Hand it an array instead and
     * the dropdown throws, which 500s every page on the site at once (#25).
     */
    public function test_every_group_handed_to_the_layout_is_a_collection(): void
    {
        $this->event('ESA 2026 Winter', 'esa-2026-winter', ['2026-02-13 10:00:00']);
        $this->event('ESA Unscheduled', 'esa-unscheduled', []);

        $this->get('/')->assertOk();

        $groups = Cache::get('menu.v2')['events'];

        $this->assertInstanceOf(Collection::class, $groups);
        $this->assertNotEmpty($groups);

        foreach ($groups as $group) {
            $this->assertInstanceOf(Collection::class, $group);
        }
    }

    /**
     * The cache lives in Postgres and outlives the deploy that changes what it
     * holds, so an ordering fix nobody can see for 24 hours is not a fix. The
     * key carries a version: a payload written by the previous release sits
     * under the previous key and is never read again.
     */
    public function test_a_menu_cached_by_the_previous_release_is_not_served(): void
    {
        $this->event('ESA 2026 Winter', 'esa-2026-winter', ['2026-02-13 10:00:00']);
        $this->event('ESA 2012', 'esa-2012', ['2012-08-16 15:00:00']);

        // What the old code left behind: ESA 2012 above the newest event, under
        // the key it wrote.
        Cache::put('menu', [
            'events' => collect(['2012' => Event::orderBy('name', 'asc')->get()]),
            'platforms' => collect(),
            'genres' => collect(),
            'categories' => collect(),
        ], 60 * 60 * 24);

        $this->assertSame(
            ['esa-2026-winter', 'esa-2012'],
            $this->dropdownSlugs($this->get('/')->getContent())
        );
    }
}
