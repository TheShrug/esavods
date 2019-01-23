<?php

namespace App\Http\Controllers;

use App\Run;
use App\Runner;
use Illuminate\Http\Request;

class RunnerController extends Controller
{
    public function runner($slug) {
	    $runner = Runner::where('slug', '=', $slug)->firstOrFail();
	    $runs = $runner->runs;
	    return view('runner', ['runs' => $runs]);
    }
}
