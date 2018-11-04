<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Run;
use App\Game;
use App\Category;
use App\Platform;
use App\Event;

class DashboardController extends Controller
{
    public function index() {
    	return view('dashboard');
    }

    public function addRun(Request $request) {
	    $run = new Run;

	    $run->platform(Platform::firstOrCreate(['name' => $request['platform']]));
	    $run->event(Event::firstOrCreate(['name' => $request['platform']]));
	    $run->youtube_vod_id = $request['youtubeId'];
	    $run->twitch_vod_id = $request['twitchId'];
	    $run->time = $request->get('time');
	    $run->game(Game::FirstOrCreate(['name' => $request['game']]));
	    $run->save();

	    $categories = $request['categories'];
	    foreach($categories as $category) {
	        $categoryModel = Category::FirstOrCreate(['name' => $category]);
	        $run->categories()->attach($categoryModel);
	    }



		return json_encode(['request'=> 'test']);
    }
}
