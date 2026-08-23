<?php

namespace App\Console\Commands;

use App\Game;
use App\Genre;
use Illuminate\Console\Command;

/**
 * The dashboard was the only thing that ever created a genre or attached one to
 * a run, and `runCsv:import` has never imported them — the CSVs have no genre
 * column. This is the replacement path: genres are a property of a game, so
 * naming a genre and the games in it covers everything the dashboard's genre
 * screens did.
 *
 *   php artisan genre:assign Platformer --game=super-metroid --game="Celeste"
 *   php artisan genre:assign Platformer --description="Jumping, mostly."
 */
class AssignGenre extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'genre:assign
                            {name : The genre name, created if it does not exist}
                            {--game=* : Slug or name of a game whose runs join the genre}
                            {--description= : Set the genre description}';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Create a genre and attach every run of the given games to it';

    /**
     * Execute the console command.
     */
    public function handle()
    {
        $genre = Genre::FirstOrCreateUniqueSlug(['name' => $this->argument('name')]);

        if ($this->option('description') !== null) {
            $genre->description = $this->option('description');
            $genre->save();
        }

        $this->info("Genre '{$genre->name}' (slug: {$genre->slug})");

        $attached = 0;

        foreach ($this->option('game') as $identifier) {
            $game = Game::where('slug', $identifier)->orWhere('name', $identifier)->first();

            if (! $game) {
                $this->error("No game matched '{$identifier}' by slug or name — skipped.");
                continue;
            }

            $runs = $game->runs;

            foreach ($runs as $run) {
                $run->genres()->syncWithoutDetaching($genre);
            }

            $attached += $runs->count();
            $this->line("  {$game->name}: {$runs->count()} run(s)");
        }

        $this->info("{$attached} run(s) now in '{$genre->name}'.");

        return self::SUCCESS;
    }
}
