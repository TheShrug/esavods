<?php

namespace App\Http\Controllers;

use App\Event;
use App\Run;
use Illuminate\Http\Request;

class EventController extends Controller
{
	/**
	 * Return the view for the runs for the event by the slug provided
	 *
	 * @param $slug
	 *
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */
	public function event($slug) {
		$event = Event::where('slug', '=', $slug)->firstOrFail();
		$runs = $event->runs;
		$title = $event->name . ' VODs - Commentated Speedrun Videos';
		$description = $event->name . ' speedrun VODs. Archive of all the commentated speedrun videos for the ' . $event->name . ' event. ' . $event->description;
		return view('event', ['runs' => $runs, 'event' => $event, 'title' => $title, 'description' => $description]);
	}

	/**
	 * Returns the view for the Event index
	 *
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */
	public function index() {
		$events = Event::withCount('runs')->get();
		return view('eventIndex', [
			'events' => $events,
			'title' => 'Events - All ESA Marathon Events',
			'description' => "Navigate through all European Speedrunner Assembly's events and select VODs to watch."
		]);
	}

}
