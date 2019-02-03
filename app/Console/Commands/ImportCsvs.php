<?php

namespace App\Console\Commands;

use App\Run;
use App\Category;
use App\Event;
use App\Platform;
use App\Runner;
use App\Game;
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
	    }
    }

    private function importCsvFile($file) {
    	$csvFile = file(storage_path('app/' .$file));
	    $csv = array_map(function($v) { return str_getcsv($v, ';'); }, $csvFile);
	    array_walk($csv, function(&$a) use ($csv) {
		    $a = array_combine($csv[0], $a);
	    });
	    array_shift($csv); # remove column header

	    foreach($csv as $runRow) {

	    	preg_match('#\[(.*?)\]#', $runRow['Game'], $nameMatches);

		    $runGame = (isset($nameMatches[1])) ? $nameMatches[1] : $runRow['Game'];
			$runDate = ($runRow['Scheduled']) ? Date('Y:m:d H:i:s', strtotime($runRow['Scheduled'])) : null;
			$runPlatform = ($runRow['Platform']) ? $runRow['Platform'] : null;
			$runEvent = ($runRow['Event']) ? $runRow['Event'] : null;
			$runCategory = ($runRow['Category']) ? $runRow['Category'] : null;
			$runCategoriesExplode = ($runRow['Categories']) ? explode('|', $runRow['Categories']) : null;
			$runPlayersExplode = ($runRow['Players']) ? explode('|', $runRow['Players']) : null;
		    $runTwitch = ($runRow['Twitch']) ? $runRow['Twitch'] : null;
		    $runYoutube = (isset($runRow['Youtube']) && !empty($runRow['Youtube'])) ? $runRow['Youtube'] : null;

		    var_dump($runGame);

		    $runRow['Time'] = str_replace('"', '', $runRow['Time']);
		    $runTimeExplode = explode(':', $runRow['Time']);
		    $runSeconds = 0;
		    $runSeconds += (int) $runTimeExplode[0] * 60 * 60;
		    $runSeconds += (int) $runTimeExplode[1] * 60;
		    $runSeconds += (int) $runTimeExplode[2];

		    $runPlayers = [];
		    if($runPlayersExplode) {
			    foreach($runPlayersExplode as $runPlayer) {
				    $runner = [];
				    preg_match('#\((.*?)\)#', $runPlayer, $playerUrlMatches);
				    preg_match('#\[(.*?)\]#', $runPlayer, $playerNameMatches);
				    if(isset($playerNameMatches[1])) $runner['name'] = $playerNameMatches[1];
				    if(isset($playerUrlMatches[1])) $runner['twitch'] = $playerUrlMatches[1];
				    array_push($runPlayers, $runner);
			    }
		    }

		    $runCategories = [];
			if($runCategoriesExplode) {
				foreach($runCategoriesExplode as $runCategoriesCategory) {
					array_push($runCategories, $runCategoriesCategory);
				}
			}

		    $game = Game::FirstOrCreateUniqueSlug(['name' => $runGame]);
		    $run = Run::firstOrNew(['game_id' => $game->id, 'category' => $runCategory]);
		    $run->game()->associate($game);

		    if($runPlatform) {
			    $platform = Platform::FirstOrCreateUniqueSlug(['name' => $runPlatform]);
			    $run->platform()->associate($platform);
		    }

		    if($runEvent) {
			    $event = Event::FirstOrCreateUniqueSlug(['name' => $runEvent]);
			    $run->event()->associate($event);
		    }

		    $run->twitch_vod_id = $runTwitch;
		    $run->youtube_vod_id = $runYoutube;
		    $run->time = $runSeconds;
		    $run->run_date = $runDate;
		    $run->category = $runCategory;
		    $run->save();

		    $categories = $runCategories;
		    $run->addCategories($categories);

		    foreach($runPlayers as $runPlayer) {
			    $runnerModel = Runner::FirstOrCreateUniqueSlug(['name' => $runPlayer['name']]);
			    if(isset($runPlayer['twitch'])) $runnerModel->twitch = $runPlayer['twitch'];
			    $runnerModel->save();
			    $run->runners()->syncWithoutDetaching($runnerModel);
		    }

		    $run->save();
	    }
    }

}
