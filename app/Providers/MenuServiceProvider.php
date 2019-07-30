<?php

namespace App\Providers;


use App\Event;
use App\Platform;
use App\Category;
use App\Genre;
use Illuminate\Support\Facades\Cache;
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
	    Cache::forget('menu');

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


    	$menu = Cache::get('menu', function() {
    		$menuArray = [];
		    $menuArray['events'] = Event::orderBy('year', 'desc')->orderBy('order', 'asc')->get()->sortByDesc('year')->groupBy('year');
	        $menuArray['platforms'] = Platform::orderBy('name', 'asc')->get();
	        $menuArray['genres'] = Genre::orderBy('name', 'asc')->get();
	        $menuArray['categories'] = Category::orderBy('name', 'asc')->get();
	        Cache::put('menu', $menuArray, 60 * 24 );
	        return $menuArray;
	    });

        view()->share('menu', $menu);
    }
}
