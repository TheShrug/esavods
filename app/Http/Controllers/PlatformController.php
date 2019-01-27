<?php

namespace App\Http\Controllers;

use App\Platform;
use App\Run;
use Illuminate\Http\Request;

class PlatformController extends Controller
{

	/**
	 * Return a view showcasing the runs on the platform slug provided
	 *
	 * @param $slug
	 *
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */
	public function platform($slug) {
		$platform = Platform::where('slug', '=', $slug)->firstOrFail();
		$runs = $platform->runs;
		$title = $platform->name . ' Commentated Speedruns - Speedruns by Platform';
		$description = 'View all commentated runs performed on the ' . $platform->name . ' at the European Speedrunner Assembly.';
		return view('platform', [
			'runs' => $runs,
			'platform' => $platform,
			'title' => $title,
			'description' => $description
		]);
	}

	/**
	 * Return the view for the platform index
	 *
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */
	public function index() {
		$platforms = Platform::get();
		return view('platformIndex', [
			'platforms' => $platforms,
			'title' => 'Platforms - All Platforms at ESA Marathon Events',
			'description' => "Navigate through all the platforms that runners used at European Speedrunner Assembly's events and select VODs to watch."
		]);
	}

}
