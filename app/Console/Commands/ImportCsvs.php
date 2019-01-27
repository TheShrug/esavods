<?php

namespace App\Console\Commands;

use App\Run;
use App\Category;
use App\Event;
use App\Platform;
use App\Runner;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Storage;

class ImportCsvs extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'runCsv:import';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Import runs from resource CSV files';

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
    	$files = Storage::disk('local')->allFiles('csv');
    	foreach($files as $file) {
    		$this->importCsvFile($file);
    		break;
	    }

//	    var_dump(date('U', strtotime('Fri 23 Nov 2018 12:00:00 +0100')));

    }

    private function importCsvFile($file) {

    	$csv = str_getcsv(Storage::disk('local')->get($file), ';');

	    var_dump(storage_path($file));

	    fopen($file, 'r');

//		$test = fopen(storage_path($file));


//    	var_dump($csv);
    }

}
