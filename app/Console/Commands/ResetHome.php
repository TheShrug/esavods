<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use App\WatchedRun;

class ResetHome extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'esavods:resetHome';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Reset the watched runs on the homepage';

    /**
     * Create a new command instance.
     *
     * @return void
     */
    public function __construct()
    {
        parent::__construct();
    }

    /**
     * Execute the console command.
     *
     * @return mixed
     */
    public function handle()
    {
        $allWatchedRuns = WatchedRun::where('old', '=', 0)->get();
        foreach ($allWatchedRuns as $run) {
            $run->old = 1;
            $run->save();
        }
    }
}
