<?php

namespace App\Http\Controllers;

use App\Game;

class GameController extends Controller
{
	/**
	 * Return runs of the game with the slug provided
	 *
	 * @param $slug
	 *
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */
    public function game($slug) {
        $game =	Game::where('slug', '=', $slug)->firstOrFail();
        $runs = $game->runs;
        $title = $game->name . ' Speedrun VODs - VODs by Game';
        $description = 'Watch speedrun VODs of ' . $game->name . ' being played at the European Speedrunner Assembly.';
		return view('game', ['runs' => $runs, 'game' => $game, 'title' => $title, 'description' => $description]);
    }

	/**
	 * Return the view for the game index page
	 *
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */
    public function index() {
		$games = Game::get();
	    return view('gameIndex', [
		    'games' => $games,
		    'title' => 'Games - All Games at ESA Marathon Events',
		    'description' => "Navigate through all the games run at European Speedrunner Assembly's events and select VODs to watch."
	    ]);
    }
}
