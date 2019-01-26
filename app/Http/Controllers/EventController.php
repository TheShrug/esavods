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

	public function index() {
		$events = Event::get();
		return view('eventIndex', [
			'events' => $events,
			'title' => 'Events - All ESA Marathon Events',
			'description' => "Navigate through all European Speedrunner Assembly's events and select VODs to watch."
		]);
	}
}
