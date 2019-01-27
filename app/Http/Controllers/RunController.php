<?php

namespace App\Http\Controllers;
use App\WatchedRun;
use App\Run;
use Illuminate\Http\Request;

class RunController extends Controller
{

	/**
	 * Create the watched run entry from post request
	 *
	 * @param Request $request
	 * @param $id
	 *
	 * @return \Illuminate\Http\JsonResponse
	 */
    public function watchedRun(Request $request, $id) {
    	$ip = $request->ip();
    	$watchedRun = WatchedRun::firstOrCreate(['run_id' => $id, 'ip' => $ip]);
    	return response()->json(['success' => true]);
    }

}
