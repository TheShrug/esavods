<?php

namespace App\Http\Controllers;

use App\Event;
use App\Run;
use Illuminate\Http\Request;

class EventController extends Controller
{
	public function event($slug) {
		$event = Event::where('slug', '=', $slug)->firstOrFail();
		$runs = $event->runs;
		return view('event', ['runs' => $runs, 'event' => $event]);
	}
}
