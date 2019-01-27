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
		               ->groupBy('run_id')
		               ->orderBy('count')
		               ->limit(100)->get();
		$ids = [];
		foreach($topRunIds as $topRun) {
			array_push($ids, $topRun->run_id);
		}
		return $ids;
	}

	protected $fillable = ['run_id', 'ip'];
}
