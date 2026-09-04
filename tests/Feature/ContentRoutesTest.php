<?php

namespace Tests\Feature;

use App\Category;
use App\Event;
use App\Game;
use App\Genre;
use App\Platform;
use App\Run;
use App\Runner;
use App\WatchedRun;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Testing\TestResponse;
use Tests\TestCase;

/**
 * Every content route, against one seeded run.
 *
 * The assertions deliberately match ROW markup rather than bare names. The
 * shared layout's nav dropdowns list every event, platform and category on
 * every page, so assertSee('GameCube') passes on a page that rendered no runs
 * at all - it would have caught nothing. The title="..." attributes and the
 * <td> fragments below appear only inside a run row.
 */
class ContentRoutesTest extends TestCase
{
    use RefreshDatabase;

    private Event $event;

    private Platform $platform;

    private Game $game;

    private Genre $genre;

    private Category $category;

    private Runner $runner;

    private Run $run;

    /**
     * Row fragments the seeded run produces, keyed by the column that renders
     * them. No two show views render the same set of columns - the game page
     * has no Platform column, for one - so each test names the columns its own
     * page actually has.
     *
     * @var array<string, string>
     */
    private const COLUMNS = [
        'game' => 'title="View all Metroid Prime runs at ESA"',
        'event' => 'title="View all ESA Winter 2026 runs"',
        'platform' => 'title="View all GameCube runs at ESA"',
        'runner' => 'title="View runs by claris"',
        'category' => '<td>Any%</td>',
        'time' => '<td>01:15:30</td>',
    ];

    protected function setUp(): void
    {
        parent::setUp();

        // Fixed names and slugs, not faked ones: the fragments above are
        // literal strings, and every show route looks its row up BY SLUG.
        $this->event = Event::factory()->create([
            'name' => 'ESA Winter 2026',
            'slug' => 'esa-winter-2026',
            'description' => 'The winter marathon.',
            'year' => 2026,
            'order' => 1,
        ]);
        $this->platform = Platform::factory()->create([
            'name' => 'GameCube',
            'slug' => 'gamecube',
            'description' => 'Nintendo GameCube.',
        ]);
        $this->game = Game::factory()->create([
            'name' => 'Metroid Prime',
            'slug' => 'metroid-prime',
            'description' => 'A first person adventure.',
        ]);
        $this->genre = Genre::factory()->create([
            'name' => 'Action Adventure',
            'slug' => 'action-adventure',
            'description' => 'Action adventure games.',
        ]);
        $this->category = Category::factory()->create([
            'name' => 'Any%',
            'slug' => 'any-percent',
            'description' => 'Finish the game by any means.',
        ]);
        $this->runner = Runner::factory()->create([
            'name' => 'claris',
            'slug' => 'claris',
        ]);

        $this->run = Run::factory()->create([
            'event_id' => $this->event->id,
            'platform_id' => $this->platform->id,
            'game_id' => $this->game->id,
            // The string column, which is what every run table prints. The
            // Category attach below is the separate relationship that
            // /category/{slug} filters on - setting one does not set the other.
            'category' => $this->category->name,
            'time' => 4530, // 01:15:30
            'run_date' => '2026-02-14 13:00:00',
        ]);

        $this->run->runners()->attach($this->runner);
        $this->run->categories()->attach($this->category);
        $this->run->genres()->attach($this->genre);
    }

    public function test_the_home_page_lists_a_watched_run(): void
    {
        // The homepage table is the top 100 WATCHED runs, not every run, so a
        // run with no watch rows renders an empty table and this test would
        // then assert nothing at all about the run.
        WatchedRun::create(['run_id' => $this->run->id, 'ip' => '127.0.0.1']);

        $response = $this->get('/');

        $response->assertOk();
        $response->assertSee('Welcome to ESA VODs');
        $this->assertRunRow($response, ['game', 'event', 'platform', 'category', 'runner', 'time']);
    }

    public function test_the_about_page_renders(): void
    {
        $response = $this->get('/about');

        $response->assertOk();
        $response->assertSee('About ESA VODs');
    }

    public function test_the_event_index_lists_the_event_and_its_run_count(): void
    {
        $response = $this->get('/event');

        $response->assertOk();
        $response->assertSee('ESA Winter 2026');
        $this->assertIndexRowCount($response, $this->event->id, 1);
    }

    public function test_the_event_page_lists_its_runs(): void
    {
        $response = $this->get('/event/esa-winter-2026');

        $response->assertOk();
        $response->assertSee('The winter marathon.', false);
        $this->assertRunRow($response, ['game', 'platform', 'category', 'runner', 'time']);
    }

    public function test_the_platform_index_lists_the_platform_and_its_run_count(): void
    {
        $response = $this->get('/platform');

        $response->assertOk();
        $response->assertSee('GameCube');
        $this->assertIndexRowCount($response, $this->platform->id, 1);
    }

    public function test_the_platform_page_lists_its_runs(): void
    {
        $response = $this->get('/platform/gamecube');

        $response->assertOk();
        $this->assertRunRow($response, ['game', 'event', 'category', 'runner', 'time']);
    }

    public function test_the_game_index_lists_the_game_and_its_run_count(): void
    {
        $response = $this->get('/game');

        $response->assertOk();
        $response->assertSee('Metroid Prime');
        $this->assertIndexRowCount($response, $this->game->id, 1);
    }

    public function test_the_game_page_lists_its_runs(): void
    {
        $response = $this->get('/game/metroid-prime');

        $response->assertOk();
        $this->assertRunRow($response, ['event', 'category', 'runner', 'time']);
    }

    public function test_the_category_index_lists_the_category_and_its_run_count(): void
    {
        $response = $this->get('/category');

        $response->assertOk();
        $response->assertSee('Any%');
        $this->assertIndexRowCount($response, $this->category->id, 1);
    }

    public function test_the_category_page_lists_its_runs(): void
    {
        $response = $this->get('/category/any-percent');

        $response->assertOk();
        $this->assertRunRow($response, ['game', 'event', 'category', 'runner', 'time']);
    }

    public function test_the_genre_index_lists_the_genre_and_its_run_count(): void
    {
        $response = $this->get('/genre');

        $response->assertOk();
        $response->assertSee('Action Adventure');
        $this->assertIndexRowCount($response, $this->genre->id, 1);
    }

    public function test_the_genre_page_lists_its_runs(): void
    {
        $response = $this->get('/genre/action-adventure');

        $response->assertOk();
        $this->assertRunRow($response, ['game', 'platform', 'event', 'category', 'runner', 'time']);
    }

    public function test_the_runner_page_lists_their_runs(): void
    {
        $response = $this->get('/runner/claris');

        $response->assertOk();
        $this->assertRunRow($response, ['game', 'platform', 'event', 'category', 'runner', 'time']);
    }

    /**
     * Every show route is a firstOrFail(), so an unknown slug must 404. Worth
     * pinning: the same miss through a broken query would be a 500, and both
     * look like "the page did not load" from outside.
     */
    public function test_an_unknown_slug_is_a_404_rather_than_a_500(): void
    {
        $paths = [
            '/event/nope',
            '/platform/nope',
            '/game/nope',
            '/category/nope',
            '/genre/nope',
            '/runner/nope',
        ];

        foreach ($paths as $path) {
            $this->get($path)->assertNotFound();
        }
    }

    /**
     * Assert the seeded run's row rendered, and that it rendered every column
     * the page under test is supposed to have.
     *
     * @param  list<string>  $columns  keys of self::COLUMNS
     */
    private function assertRunRow(TestResponse $response, array $columns): void
    {
        $response->assertSee('data-id="'.$this->run->id.'"', false);

        foreach ($columns as $column) {
            $response->assertSee(self::COLUMNS[$column], false);
        }
    }

    /**
     * Assert an index page's row for $id carries the withCount() total. The
     * count is the only cell on those pages holding a bare number, so matching
     * a whole cell keeps this from passing on the row's own data-id.
     */
    private function assertIndexRowCount(TestResponse $response, int $id, int $count): void
    {
        $html = $response->getContent();

        $start = strpos($html, '<tr data-id="'.$id.'">');
        $this->assertNotFalse($start, "the index rendered no row for id {$id}");

        $row = substr($html, $start, strpos($html, '</tr>', $start) - $start);
        $this->assertMatchesRegularExpression("/<td>\s*{$count}\s*<\/td>/", $row);
    }
}
