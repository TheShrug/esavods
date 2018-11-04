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
}
