<?php

namespace App\Providers;


use App\Event;
use App\Platform;
use App\Category;
use App\Genre;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\View;
use Illuminate\Support\ServiceProvider;

class MenuServiceProvider extends ServiceProvider
{
    /**
     * Bootstrap services.
     *
     * @return void
     */
    public function boot()
    {
        // all of this should probably be different, but there is no time!
        Event::saved(function() {
            Cache::forget('menu');
        });
        Platform::saved(function() {
            Cache::forget('menu');
        });
        Category::saved(function() {
            Cache::forget('menu');
        });
        Genre::saved(function() {
            Cache::forget('menu');
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
        return Cache::get('menu', function() {
            $menuArray = [];
            $menuArray['events'] = Event::orderBy('year', 'desc')->orderBy('order', 'asc')->get()->sortByDesc('year')->groupBy('year');
            $menuArray['platforms'] = Platform::orderBy('name', 'asc')->get();
            $menuArray['genres'] = Genre::orderBy('name', 'asc')->get();
            $menuArray['categories'] = Category::orderBy('name', 'asc')->get();
            // 24 hours. Laravel 5.8 changed this argument from minutes to seconds,
            // so the 5.7 value of `60 * 24` would now mean 24 minutes.
            Cache::put('menu', $menuArray, 60 * 60 * 24);
            return $menuArray;
        });
    }
}
