<?php

namespace App\Http\Controllers;

use App\Run;
use Illuminate\Http\Request;

class HomeController extends Controller
{

    /**
     * Show the application dashboard.
     *
     * @return \Illuminate\Http\Response
     */
    public function index()
    {
	    $runs = Run::with('categories', 'game', 'platform', 'runners', 'event')->get();
        return view('home', ['runs' => $runs, 'title' => 'Welcome to ESA Vods']);
    }

    public function about() {
    	$title = 'About ESA Vods - Speedrun Marathon Vods';
    	$description = 'This site contains an archive of all known speedruns at the European Speedrunner Assembly Marathon. All credit belongs to ESA and the speedrunners involved.';
    	return view('about', ['title' => $title, 'description' => $description]);
}
}
