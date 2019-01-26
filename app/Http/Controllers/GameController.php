<?php

namespace App\Http\Controllers;

use App\Game;
use App\Run;
use Illuminate\Http\Request;

class GameController extends Controller
{
    public function game($slug) {
        $game =	Game::where('slug', '=', $slug)->firstOrFail();
        $runs = $game->runs;
		return view('game', ['runs' => $runs, 'game' => $game]);
    }
}
