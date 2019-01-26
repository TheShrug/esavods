<?php

namespace App\Http\Controllers;

use App\Run;
use App\Genre;
use Illuminate\Http\Request;

class GenreController extends Controller
{
	public function genre($slug) {
		$genre = Genre::where('slug', '=', $slug)->firstOrFail();
		$runs = $genre->runs;
		return view('genre', ['runs' => $runs, 'genre' => $genre]);
	}

	/**
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */
	public function index() {
		$genres = Genre::get();
		return view('genreIndex', [
			'genres' => $genres,
			'title' => 'Genres - All Game Genres at ESA Marathon Events',
			'description' => "Navigate through all the genres of games at European Speedrunner Assembly's events and select VODs to watch."
		]);
	}
}
