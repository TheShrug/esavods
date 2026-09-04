<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use PHPUnit\Framework\Attributes\DataProvider;
use Tests\TestCase;

/**
 * The permanent redirects at the top of routes/web.php.
 *
 * These are the URLs the site published before events and platforms were
 * renamed. They are 301s, so browsers and search engines have cached them for
 * years - deleting one does not un-publish it, it just starts returning 404 to
 * traffic that is still arriving. Nothing here needs seeding: a redirect route
 * returns before any query runs. RefreshDatabase is here only so the wildcard
 * comparison at the bottom has a schema to miss against.
 */
class LegacyRedirectTest extends TestCase
{
    use RefreshDatabase;

    /**
     * @return array<string, array{string, string}>
     */
    public static function redirects(): array
    {
        return [
            'esa-2019-one' => ['/event/esa-2019-one', '/event/esa-2019-summer-one'],
            'esa-2019-two' => ['/event/esa-2019-two', '/event/esa-2019-summer-two'],
            'esa-2018' => ['/event/esa-2018', '/event/esa-2018-summer-one'],
            'esa-2018-two' => ['/event/esa-2018-two', '/event/esa-2018-summer-two'],
            'gp-player' => ['/platform/gp-player', '/platform/game-boy'],
            'gb' => ['/platform/gb', '/platform/game-boy'],
            'gameboy-player' => ['/platform/gameboy-player', '/platform/game-boy'],
            'gpp' => ['/platform/gpp', '/platform/game-boy'],
            'gc' => ['/platform/gc', '/platform/gamecube'],
            'gcn' => ['/platform/gcn', '/platform/gamecube'],
            'gba' => ['/platform/gba', '/platform/game-boy-advance'],
            'gba-emu' => ['/platform/gba-emu', '/platform/game-boy-advance'],
            'gbs-emu' => ['/platform/gbs-emu', '/platform/game-boy-advance'],
        ];
    }

    #[DataProvider('redirects')]
    public function test_it_redirects_permanently(string $from, string $to): void
    {
        $response = $this->get($from);

        // 301, not just "a redirect": a 302 here would work in a browser and
        // still lose the accumulated search ranking these URLs carry.
        $response->assertStatus(301);
        $response->assertRedirect($to);
    }

    /**
     * The redirect targets are declared ahead of `/platform/{slug}` and
     * `/event/{slug}`, so they win the match. This pins that ordering: move
     * them below the wildcards and every one of them starts 404ing instead,
     * which the status assertion above would not distinguish from a typo.
     */
    public function test_the_redirects_are_matched_before_the_wildcard_routes(): void
    {
        $this->get('/platform/gb')->assertStatus(301);
        $this->get('/platform/not-a-redirect')->assertNotFound();
    }
}
