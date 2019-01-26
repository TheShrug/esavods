<?php

namespace App\Http\Controllers;

use App\Platform;
use App\Run;
use Illuminate\Http\Request;

class PlatformController extends Controller
{
	public function platform($slug) {
		$platform = Platform::where('slug', '=', $slug)->firstOrFail();
		$runs = $platform->runs;
		return view('platform', ['runs' => $runs, 'platform' => $platform]);
	}

	public function index() {
		$platforms = Platform::get();
		return view('platformIndex', [
			'platforms' => $platforms,
			'title' => 'Platforms - All Platforms at ESA Marathon Events',
			'description' => "Navigate through all the platforms that runners used at European Speedrunner Assembly's events and select VODs to watch."
		]);
	}
}
