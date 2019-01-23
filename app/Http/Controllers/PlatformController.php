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
		return view('platform', ['runs' => $runs]);
	}
}
