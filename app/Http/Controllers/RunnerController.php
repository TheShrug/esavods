<?php

namespace App\Http\Controllers;

use App\Run;
use App\Runner;
use Illuminate\Http\Request;

class RunnerController extends Controller
{

	/**
	 * Return the view for the runner by the provided slug
	 *
	 * @param $slug
	 *
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */
    public function runner($slug) {
	    $runner = Runner::where('slug', '=', $slug)->firstOrFail();
	    $runs = $runner->runs;
	    $title = 'Runs by ' . $runner->name . ' at ESA - VODs by Runner';
	    $description = 'View all runs performed by ' . $runner->name . ' at the European Speedrunner Assembly and make sure to follow them!';
	    return view('runner', [
	    	'runs' => $runs,
		    'runner' => $runner,
		    'title' => $title,
		    'description' => $description
	    ]);
    }

}
