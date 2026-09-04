<?php

namespace Tests\Feature;

use App\Category;
use App\Event;
use App\Game;
use App\Genre;
use App\Platform;
use App\Run;
use App\Runner;
use Illuminate\Foundation\Testing\RefreshDatabase;
use PHPUnit\Framework\Attributes\DataProvider;
use Tests\TestCase;

/**
 * The pages nobody looks at, on data nobody has.
 *
 * Every controller hands its view a `$runs` collection and every view guards
 * on `@if($runs)` - which is an object test, so the guard is always true and
 * the empty branch is the @foreach body never running. That branch is what
 * these cover, plus the harder one: a completely empty database, where the
 * shared layout still has to build a nav out of nothing. The platforms
 * dropdown divides by the platform count to lay itself out in three columns,
 * and a zero there would 500 every page on the site at once.
 */
class EmptyStateTest extends TestCase
{
    use RefreshDatabase;

    /**
     * @return array<string, array{string}>
     */
    public static function indexRoutes(): array
    {
        return [
            'home' => ['/'],
            'about' => ['/about'],
            'events' => ['/event'],
            'platforms' => ['/platform'],
            'games' => ['/game'],
            'categories' => ['/category'],
            'genres' => ['/genre'],
        ];
    }

    #[DataProvider('indexRoutes')]
    public function test_it_renders_on_an_empty_database(string $path): void
    {
        $this->get($path)->assertOk();
    }

    public function test_an_event_with_no_runs_renders(): void
    {
        Event::factory()->create(['slug' => 'quiet-event']);

        $this->get('/event/quiet-event')->assertOk();
    }

    public function test_a_platform_with_no_runs_renders(): void
    {
        Platform::factory()->create(['slug' => 'quiet-platform']);

        $this->get('/platform/quiet-platform')->assertOk();
    }

    public function test_a_game_with_no_runs_renders(): void
    {
        Game::factory()->create(['slug' => 'quiet-game']);

        $this->get('/game/quiet-game')->assertOk();
    }

    public function test_a_category_with_no_runs_renders(): void
    {
        Category::factory()->create(['slug' => 'quiet-category']);

        $this->get('/category/quiet-category')->assertOk();
    }

    public function test_a_genre_with_no_runs_renders(): void
    {
        Genre::factory()->create(['slug' => 'quiet-genre']);

        $this->get('/genre/quiet-genre')->assertOk();
    }

    public function test_a_runner_with_no_runs_and_no_socials_renders(): void
    {
        Runner::factory()->withoutSocials()->create(['slug' => 'quiet-runner']);

        $this->get('/runner/quiet-runner')->assertOk();
    }

    /**
     * A run whose event, platform, game, runners and VOD ids are all missing.
     * Every one of those columns is behind an `@if(isset(...))` in the run
     * tables, and the import has produced rows like this before.
     */
    public function test_a_run_with_no_relations_and_no_vods_renders(): void
    {
        $event = Event::factory()->create(['slug' => 'sparse-event']);

        Run::factory()->withoutVods()->create([
            'event_id' => $event->id,
            'platform_id' => null,
            'game_id' => null,
            'category' => null,
            'run_date' => null,
        ]);

        $this->get('/event/sparse-event')->assertOk();
    }
}
