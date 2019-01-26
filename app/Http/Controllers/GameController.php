<?php

namespace App\Http\Controllers;

use App\Game;

class GameController extends Controller
{
    public function game($slug) {
        $game =	Game::where('slug', '=', $slug)->firstOrFail();
        $runs = $game->runs;
		return view('game', ['runs' => $runs, 'game' => $game]);
    }

    public function index() {
		$games = Game::get();
	    return view('gameIndex', [
		    'games' => $games,
		    'title' => 'Games - All Games at ESA Marathon Events',
		    'description' => "Navigate through all the games run at European Speedrunner Assembly's events and select VODs to watch."
	    ]);
    }
}
