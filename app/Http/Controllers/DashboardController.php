<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Run;
use App\Game;
use App\Category;
use App\Platform;
use App\Event;
use App\Runner;
use App\Genre;
use Storage;
use League\Csv\Reader;

class DashboardController extends Controller
{
    public function index() {
    	return view('dashboard', array('dashboard' => true));
    }

    public function uploadCsv(Request $request) {
		$path = $request->file('file')->store('uploads');

		$file = Storage::get($path);


		$csv = Reader::createFromString($file);
		$csv->setHeaderOffset(0);
		$csv->setDelimiter(';');

		$records = $csv->getRecords();

		foreach($records as $record) {

			$platform = Platform::FirstOrCreateUniqueSlug(['name' => $record['Platform']]);
			$event = Event::FirstOrCreateUniqueSlug(['name' => $record['Event']]);
			$game = Game::FirstOrCreateUniqueSlug(['name' => $record['Game']]);

			$run = Run::firstOrNew(['game_id' => $game->id, 'category' => $record['Category'], 'run_date' => date("Y-m-d H:i:s", strtotime($record['Schedule']))]);

			$run->platform()->associate($platform);
			$run->event()->associate($event);
			$run->game()->associate($game);

			if($record['Twitch']) {
				$run->twitch_vod_id = $record['Twitch'];
			}
			if($record['Youtube']) {
				$run->youtube_vod_id = $record['Youtube'];
			}
			$run->time = $record['Time'];
			$run->run_date = date("Y-m-d H:i:s", strtotime($record['Schedule']));
			$run->category = $record['Category'];
			$run->save();

			$categories = array($record['Extra']);
			$run->addCategories($categories);

			preg_match_all('/\[(.*?)\]\((.*?)\)/', $record['Runners'], $runnersRegexOutput);

			$runnersArray = [];
			if(!empty($runnersRegexOutput)) {
				foreach($runnersRegexOutput[1] as $key => $name) {
					$runnersArray[] = ['name' => $name, 'twitch' => $runnersRegexOutput[2][$key]];
				}
			}

			$run->addRunnersImport($runnersArray);

		}

    }

    public function addOrUpdateRun(Request $request) {
	    $run = new Run;

	    if($request['platform']) {
		    $platform = Platform::FirstOrCreateUniqueSlug(['name' => $request['platform']]);
			$run->platform()->associate($platform);
	    }

	    if($request['event']) {
		    $event = Event::FirstOrCreateUniqueSlug(['name' => $request['event']]);
		    $run->event()->associate($event);
	    }

	    if($request['game']) {
		    $game = Game::FirstOrCreateUniqueSlug(['name' => $request['game']]);
		    $run->game()->associate($game);
	    }

	    $run->youtube_vod_id = $request['youtubeId'];
	    $run->twitch_vod_id = $request['twitchId'];
	    $run->time = $request->get('time');
	    $run->run_date = $request->get('datetime');
	    $run->category = $request->get('runCategory');
	    $run->save();

	    $categories = $request['categories'];
	    $run->addCategories($categories);

	    $runners = $request['runners'];
	    $run->addRunners($runners);

	    $genres = $request['genres'];
	    $run->addGenres($genres);


		return response()->json(self::formatForJson());

    }

    public function editRun(Request $request) {

	    $run = Run::findOrFail($request['id']);

	    $run->platform()->dissociate();
	    if($request['platform']) {
		    $platform = Platform::FirstOrCreateUniqueSlug(['name' => $request['platform']]);
		    $run->platform()->associate($platform);
	    }

	    $run->event()->dissociate();
	    if($request['event']) {
		    $event = Event::FirstOrCreateUniqueSlug(['name' => $request['event']]);
		    $run->event()->associate($event);
	    }

	    $run->game()->dissociate();
	    if($request['game']) {
		    $game = Game::FirstOrCreateUniqueSlug(['name' => $request['game']]);
		    $run->game()->associate($game);
	    }

	    $run->youtube_vod_id = $request['youtubeId'];
	    $run->twitch_vod_id = $request['twitchId'];
	    $run->time = $request->get('time');
	    $run->run_date = $request->get('datetime');
	    $run->category = $request->get('runCategory');
	    $run->categories()->detach();
	    $run->genres()->detach();
	    $run->runners()->detach();
	    $run->save();

	    $categories = $request['categories'];
	    $run->addCategories($categories);

	    $runners = $request['runners'];
	    $run->addRunners($runners);

	    $genres = $request['genres'];
	    $run->addGenres($genres);

	    return response()->json(self::formatForJson());
    }

    public function deleteRun(Request $request) {
	    $run = Run::findOrFail($request['id']);
	    $run->delete();
	    return response()->json(self::formatForJson());
    }
	public function deleteGame(Request $request) {
		$game = Game::findOrFail($request['id']);
		$game->delete();
		return response()->json(self::formatForJson());
	}

	public function deleteRunner(Request $request) {
		$runner = Runner::findOrFail($request['id']);
		$runner->delete();
		return response()->json(self::formatForJson());
	}

	public function deleteEvent(Request $request) {
		$event = Event::findOrFail($request['id']);
		$event->delete();
		return response()->json(self::formatForJson());
	}

	public function deleteCategory(Request $request) {
		$category = Category::findOrFail($request['id']);
		$category->delete();
		return response()->json(self::formatForJson());
	}

	public function deletePlatform(Request $request) {
		$platform = Platform::findOrFail($request['id']);
		$platform->delete();
		return response()->json(self::formatForJson());
	}

	public function deleteGenre(Request $request) {
		$genre = Genre::findOrFail($request['id']);
		$genre->delete();
		return response()->json(self::formatForJson());
	}

    public static function formatForJson($page = 1) {
    	$json = [];
	    $json['categories'] = Category::all();
	    $json['games'] = Game::all();
	    $json['platforms'] = Platform::all();
	    $json['events'] = Event::all();
	    $json['runners'] = Runner::all();
	    $json['genres'] = Genre::all();
	    $json['runs'] = Run::with('categories', 'genres', 'game', 'platform', 'runners', 'event')->orderBy('id', 'DESC')->paginate(20, null, 'page', $page);
		return $json;
    }

    public static function getJson() {
    	return response()->json(self::formatForJson());
    }

    public static function getRunsPaginated($page) {
    	return Run::orderBy('id', 'DESC')->paginate(20, null, 'page', $page);
    }

    public static function getRunsJson(Request $request) {
    	$page = $request['page'];
    	return response()->json(self::getRunsPaginated($page));
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

	// Genres
	public static function addGenre(Request $request) {
		$genre = Genre::firstOrCreate([
			'name' => $request['genre'],
			'slug' => $request['slug'],
			'description' => $request['description']
		]);
		$genre->save();
		return self::getGenres();
	}

	public static function editGenre(Request $request) {
		$genre = Genre::findOrFail($request['id']);
		$genre->name = $request['name'];
		$genre->slug = $request['slug'];
		$genre->description = $request['description'];
		$genre->save();
		return self::getGenres();
	}

	public static function getGenres() {
		return response()->json(['genres' => Genre::all()]);
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
