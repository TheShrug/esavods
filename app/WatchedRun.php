<?php

namespace App;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\DB;

/**
 * App\WatchedRun
 *
 * @property int $id
 * @property int $run_id
 * @property string $ip
 * @property \Illuminate\Support\Carbon|null $created_at
 * @property \Illuminate\Support\Carbon|null $updated_at
 * @method static \Illuminate\Database\Eloquent\Builder|\App\WatchedRun whereCreatedAt($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\WatchedRun whereId($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\WatchedRun whereIp($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\WatchedRun whereRunId($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\WatchedRun whereUpdatedAt($value)
 * @mixin \Eloquent
 */
class WatchedRun extends Model
{

	/**
	 * Get the top 100 watched run ids
	 *
	 * @return array
	 */
	public static function getTopWatchedRunIds() {
		$topRunIds = DB::table('watched_runs')
		               ->select(DB::raw('run_id, count(*) as count'))
			           ->where('old', '=', 0)
		               ->groupBy('run_id')
		               ->orderBy('count')
		               ->limit(100)->get();
		$ids = [];
		foreach($topRunIds as $topRun) {
			array_push($ids, $topRun->run_id);
		}
		return $ids;
	}

	/**
	 * Retire every counting watch older than $cutoff, and report how many.
	 *
	 * Lives here rather than inside the migration that calls it so the reset
	 * has one definition. A migration body cannot be exercised by a test - by
	 * the time a test has rows to reset, its migrations have long since run
	 * against an empty table - so a copy of this query in the test suite would
	 * be asserting on itself, and would keep passing after the real one changed.
	 *
	 * Rows already flagged are skipped, which makes a second call a no-op
	 * rather than a rewrite of the table. A row with no created_at is treated
	 * as older than any cutoff: it cannot be shown to be recent, and these
	 * predate the timestamps being reliably populated.
	 */
	public static function retireWatchesBefore(string $cutoff): int {
		return DB::table('watched_runs')
		         ->where('old', '=', 0)
		         ->where(function($query) use ($cutoff) {
			         $query->where('created_at', '<', $cutoff)
			               ->orWhereNull('created_at');
		         })
		         ->update(['old' => 1]);
	}

	protected $fillable = ['run_id', 'ip'];
}
