<?php

namespace App\Http\Controllers;

use App\Game;
use App\Run;
use Illuminate\Http\Request;

class GameController extends Controller
{
    public function game($slug) {
        $game =	Game::where('slug', '=', $slug)->firstOrFail();
        $runs = Run::where('game_id', '=', $game->id)->get();
		return view('game', ['runs' => $runs]);
    }
}
