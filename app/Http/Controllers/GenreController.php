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
}
