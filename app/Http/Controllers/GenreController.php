<?php

namespace App\Http\Controllers;

use App\Run;
use App\Genre;
use Illuminate\Http\Request;

class GenreController extends Controller
{
	/**
	 * Return all runs within a genre by slug
	 *
	 * @param $slug
	 *
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */
	public function genre($slug) {
		$genre = Genre::where('slug', '=', $slug)->firstOrFail();
		$runs = $genre->runs;
		$title = $genre->name . ' Speedrun VODs - VODs by Genre';
		$description = 'Watch speedrun VODs within the ' . $genre->name .' genre at European Speedrunner Assembly.';
		return view('genre', ['runs' => $runs, 'genre' => $genre, 'title' => $title, 'description' => $description]);
	}

	/**
	 * Return all genres
	 *
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */
	public function index() {
		$genres = Genre::withCount('runs')->get();
		return view('genreIndex', [
			'genres' => $genres,
			'title' => 'Genres - All Game Genres at ESA Marathon Events',
			'description' => "Navigate through all the genres of games at European Speedrunner Assembly's events and select VODs to watch."
		]);
	}
}
