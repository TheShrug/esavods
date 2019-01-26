<?php

namespace App\Providers;

use App\Event;
use App\Platform;
use App\Category;
use App\Genre;
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
    	$menu = [];
    	$menu['events'] = Event::orderBy('name', 'asc')->get();
    	$menu['platforms'] = Platform::orderBy('name', 'asc')->get();
    	$menu['genres'] = Genre::orderBy('name', 'asc')->get();
    	$menu['categories'] = Category::orderBy('name', 'asc')->get();
        view()->share('menu', $menu);
    }
}
