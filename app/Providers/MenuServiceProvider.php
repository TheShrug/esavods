<?php

namespace App\Providers;


use App\Event;
use App\Platform;
use App\Category;
use App\Genre;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\View;
use Illuminate\Support\ServiceProvider;

class MenuServiceProvider extends ServiceProvider
{
    /**
     * The cache key, versioned deliberately.
     *
     * The menu is cached for 24 hours in the `cache` table, which lives in
     * Postgres and survives a deploy — so a release that changes what menu()
     * builds keeps serving the payload built by the previous release until it
     * expires (#98). Model saves clear the key, but a code-only change has no
     * save to hang off. Bump the version whenever the ordering, the grouping
     * or the shape of the cached array changes, and the old entry is simply
     * never read again.
     */
    private const CACHE_KEY = 'menu.v2';

    /**
     * Bootstrap services.
     *
     * @return void
     */
    public function boot()
    {
        // all of this should probably be different, but there is no time!
        Event::saved(function() {
            Cache::forget(self::CACHE_KEY);
        });
        Platform::saved(function() {
            Cache::forget(self::CACHE_KEY);
        });
        Category::saved(function() {
            Cache::forget(self::CACHE_KEY);
        });
        Genre::saved(function() {
            Cache::forget(self::CACHE_KEY);
        });

        // Laravel 5.7 built the menu right here in boot() and view()->share()d it,
        // behind a Schema::hasTable('migrations') guard. That meant a database
        // round trip on every request *and* every console command, and it threw
        // when the database was unreachable — which took out `composer install`
        // (package:discover) and every artisan command on a host with no database.
        // Building it when a view is actually rendered gives the same menu on
        // every page with none of that.
        View::composer('*', function ($view) {
            $view->with('menu', $this->menu());
        });
    }

    /**
     * The cached navigation menu.
     */
    protected function menu(): array
    {
        // 24 hours. Laravel 5.8 changed this argument from minutes to seconds,
        // so the 5.7 value of `60 * 24` would now mean 24 minutes.
        $menu = Cache::remember(self::CACHE_KEY, 60 * 60 * 24, function() {
            return [
                'events' => $this->events(),
                'platforms' => Platform::orderBy('name', 'asc')->get(),
                'genres' => Genre::orderBy('name', 'asc')->get(),
                'categories' => Category::orderBy('name', 'asc')->get(),
            ];
        });

        // A blank slug makes route('*.show') throw. This menu renders in the shared
        // layout, so one bad row 500s every page (#25, the 2026-08-25 outage).
        // Filtered on read, not inside the closure: the cache lives in Postgres and
        // survives deploys, so a cache warmed before this fix still holds bad rows.
        $menu['categories'] = collect($menu['categories'])
            ->filter(fn ($c) => filled($c->slug))->values();

        $menu['platforms'] = collect($menu['platforms'])
            ->filter(fn ($p) => filled($p->slug))->values();

        // events is grouped and each group has ->chunk(2) called on it in the
        // layout, so each group must stay a Collection. Drop groups left empty.
        $menu['events'] = collect($menu['events'])
            ->map(fn ($group) => collect($group)->filter(fn ($e) => filled($e->slug))->values())
            ->reject(fn ($group) => $group->isEmpty());

        return $menu;
    }

    /**
     * Every event, newest first, grouped for the layout's separators.
     *
     * An event's date is MIN(run_date) over its runs. That column is written by
     * the CSV importer from the schedule's `Scheduled` field and has been since
     * the 2012 files, so it needs no data entry and cannot be forgotten — which
     * `events.year` and `events.order` could and were, leaving every event
     * added since 2019 in a NULL tail at the bottom of the dropdown (#98).
     * It also sorts Winter against Summer of the same year correctly, which a
     * year alone cannot.
     *
     * The alias is what withMin() names the subquery; Postgres resolves a bare
     * identifier in ORDER BY to an output column. NULLS LAST is not optional:
     * Postgres sorts NULLs FIRST under DESC, which would put an event whose
     * runs have no date at the very top. Those events sort to the bottom
     * instead, by name so the order is at least stable — there is nothing
     * better to say about an event nothing is known to have aired at.
     *
     * The group key is never rendered. The layout groups only to draw an <hr>
     * between groups, so keying on the calendar year puts a separator between
     * one year and the next, and every group is a Collection for ->chunk(2).
     */
    protected function events(): Collection
    {
        return Event::withMin('runs', 'run_date')
            ->orderByRaw('runs_min_run_date desc nulls last')
            ->orderBy('name', 'asc')
            ->get()
            ->groupBy(function(Event $event) {
                // A raw aggregate, so a 'Y-m-d H:i:s' string rather than a date
                // object: this model casts nothing.
                return $event->runs_min_run_date
                    ? substr($event->runs_min_run_date, 0, 4)
                    : 'undated';
            });
    }
}
