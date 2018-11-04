<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Run;
use App\Game;
use App\Category;
use App\Platform;
use App\Event;
use App\Runner;

class DashboardController extends Controller
{
    public function index() {
    	return view('dashboard');
    }

    public function addOrUpdateRun(Request $request) {
	    $run = new Run;

	    if($request['platform']) {
		    $platform = Platform::firstOrCreate(['name' => $request['platform']]);
			$run->platform()->associate($platform);
	    }

	    if($request['event']) {
		    $event = Event::firstOrCreate(['name' => $request['event']]);
		    $run->event()->associate($event);
	    }

	    if($request['game']) {
		    $game = Game::firstOrCreate(['name' => $request['game']]);
		    $run->game()->associate($game);
	    }

	    $run->youtube_vod_id = $request['youtubeId'];
	    $run->twitch_vod_id = $request['twitchId'];
	    $run->time = $request->get('time');
	    $run->category = $request->get('runCategory');
	    $run->save();

	    // Create the many-to-many models and attach
	    $categories = $request['categories'];
	    foreach($categories as $category) {
	        $categoryModel = Category::FirstOrCreate(['name' => $category]);
	        $run->categories()->attach($categoryModel);
	    }

	    $runners = $request['runners'];
	    foreach($runners as $runner) {
		    $runnerModel = Runner::FirstOrCreate(['name' => $runner]);
		    $run->runners()->attach($runnerModel);
	    }

		return response()->json(self::formatForJson());

    }

    public function editRun(Request $request) {

	    $run = Run::findOrFail($request['id']);

	    $run->platform()->dissociate();
	    if($request['platform']) {
		    $platform = Platform::firstOrCreate(['name' => $request['platform']]);
		    $run->platform()->associate($platform);
	    }

	    $run->event()->dissociate();
	    if($request['event']) {
		    $event = Event::firstOrCreate(['name' => $request['event']]);
		    $run->event()->associate($event);
	    }

	    $run->game()->dissociate();
	    if($request['game']) {
		    $game = Game::firstOrCreate(['name' => $request['game']]);
		    $run->game()->associate($game);
	    }

	    $run->youtube_vod_id = $request['youtubeId'];
	    $run->twitch_vod_id = $request['twitchId'];
	    $run->time = $request->get('time');
	    $run->category = $request->get('runCategory');
	    $run->categories()->detach();
	    $run->runners()->detach();
	    $run->save();

	    // Create the many-to-many models and attach
	    $categories = $request['categories'];
	    foreach($categories as $category) {
		    $categoryModel = Category::FirstOrCreate(['name' => $category]);
		    $run->categories()->attach($categoryModel);
	    }

	    $runners = $request['runners'];
	    foreach($runners as $runner) {
		    $runnerModel = Runner::FirstOrCreate(['name' => $runner]);
		    $run->runners()->attach($runnerModel);
	    }

	    return response()->json(self::formatForJson());
    }

    public static function formatForJson() {
    	$json = [];
	    $json['categories'] = Category::all();
	    $json['games'] = Game::all();
	    $json['platforms'] = Platform::all();
	    $json['events'] = Event::all();
	    $json['runners'] = Runner::all();
	    $json['runs'] = Run::with('categories', 'game', 'platform', 'runners', 'event')->get();
		return $json;
    }

    public static function getJson() {
    	return response()->json(self::formatForJson());
    }

    // Categories
    public static function addCategory(Request $request) {
    	$category = Category::firstOrCreate([
			'name' => $request['category'],
			'slug' => $request['slug'],
			'description' => $request['description']
	    ]);
    	$category->save();
    	return self::getCategories();
    }

    public static function editCategory(Request $request) {
    	$category = Category::findOrFail($request['id']);
    	$category->name = $request['name'];
    	$category->slug = $request['slug'];
    	$category->description = $request['description'];
    	$category->save();
	    return self::getCategories();
    }

    public static function getCategories() {
    	return response()->json(['categories' => Category::all()]);
    }

    // Events
	public static function addEvent(Request $request) {
		$event = Event::firstOrCreate([
			'name' => $request['event'],
			'slug' => $request['slug'],
			'description' => $request['description']
		]);
		$event->save();
		return self::getEvents();
	}

	public static function editEvent(Request $request) {
		$event = Event::findOrFail($request['id']);
		$event->name = $request['name'];
		$event->slug = $request['slug'];
		$event->description = $request['description'];
		$event->save();
		return self::getEvents();
	}

	public static function getEvents() {
		return response()->json(['events' => Event::all()]);
	}

	// Platforms
	public static function addPlatform(Request $request) {
		$platform = Platform::firstOrCreate([
			'name' => $request['platform'],
			'slug' => $request['slug'],
			'description' => $request['description']
		]);
		$platform->save();
		return self::getPlatforms();
	}

	public static function editPlatform(Request $request) {
		$platform = Platform::findOrFail($request['id']);
		$platform->name = $request['name'];
		$platform->slug = $request['slug'];
		$platform->description = $request['description'];
		$platform->save();
		return self::getPlatforms();
	}

	public static function getPlatforms() {
		return response()->json(['platforms' => Platform::all()]);
	}

	// Games
	public static function addGame(Request $request) {
		$game = Game::firstOrCreate([
			'name' => $request['game'],
			'slug' => $request['slug'],
			'description' => $request['description']
		]);
		$game->save();
		return self::getGames();
	}

	public static function editGame(Request $request) {
		$game = Game::findOrFail($request['id']);
		$game->name = $request['name'];
		$game->slug = $request['slug'];
		$game->description = $request['description'];
		$game->save();
		return self::getGames();
	}

	public static function getGames() {
		return response()->json(['games' => Game::all()]);
	}

	// Runners
	public static function addRunner(Request $request) {
		$runner = Runner::firstOrCreate([
			'name' => $request['runner'],
			'slug' => $request['slug'],
			'twitch' => $request['twitch'],
			'twitter' => $request['twitter'],
			'youtube' => $request['youtube']
		]);
		$runner->save();
		return self::getRunners();
	}

	public static function editRunner(Request $request) {
		$runner = Runner::findOrFail($request['id']);
		$runner->name = $request['name'];
		$runner->slug = $request['slug'];
		$runner->twitch = $request['twitch'];
		$runner->twitter = $request['twitter'];
		$runner->youtube = $request['youtube'];
		$runner->save();
		return self::getRunners();
	}

	public static function getRunners() {
		return response()->json(['runners' => Runner::all()]);
	}

}
