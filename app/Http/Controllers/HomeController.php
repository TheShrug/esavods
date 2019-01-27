<?php

namespace App\Http\Controllers;

use App\Run;
use App\WatchedRun;
use Illuminate\Http\Request;

class HomeController extends Controller
{

	/**
	 * Show the index on the homepage
	 *
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */
    public function index()
    {
    	// todo: might want to cache these
	    $topRunIds = WatchedRun::getTopWatchedRunIds();
	    $runs = Run::getRunsByIdArray($topRunIds);
        return view('home', [
        	'runs' => $runs,
	        'title' => 'ESA VODs - European Speedrunner Assembly',
	        'description' => 'ESA VODs is a website that archives European Speedrunner Assembly VODs. Go back and watch all of the runs that you might have missed.'
        ]);
    }

	/**
	 *
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */
    public function about() {
    	$title = 'About ESA VODs - Speedrun Marathon VODs';
    	$description = 'This site contains an archive of all known speedruns at the European Speedrunner Assembly Marathon. All credit belongs to ESA and the speedrunners involved.';
    	return view('about', ['title' => $title, 'description' => $description]);
	}

}
