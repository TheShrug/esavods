<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

/**
 * App\Run
 *
 * @property-read \Illuminate\Database\Eloquent\Collection|\App\Category[] $categories
 * @property-read \App\Event $event
 * @property-read \App\Game $game
 * @property-read \App\Platform $platform
 * @property-read \Illuminate\Database\Eloquent\Collection|\App\Runner[] $runners
 * @mixin \Eloquent
 * @property int $id
 * @property float $time
 * @property string|null $twitch_vod_id
 * @property string|null $youtube_vod_id
 * @property int|null $event_id
 * @property int|null $platform_id
 * @property int|null $game_id
 * @property \Illuminate\Support\Carbon|null $created_at
 * @property \Illuminate\Support\Carbon|null $updated_at
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Run whereCreatedAt($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Run whereEventId($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Run whereGameId($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Run whereId($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Run wherePlatformId($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Run whereTime($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Run whereTwitchVodId($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Run whereUpdatedAt($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Run whereYoutubeVodId($value)
 * @property string|null $category
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Run whereCategory($value)
 * @property string|null $run_date
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Run whereRunDate($value)
 */
class Run extends Model
{

	/**
	 * @param array $runners
	 */
	public function addRunners(array $runners) {
		if($runners) {
			foreach($runners as $runner) {
				$runnerModel = Runner::FirstOrCreateUniqueSlug(['name' => $runner]);
				$this->runners()->attach($runnerModel);
			}
		}
	}

	public function addCategories(array $categories) {
		if($categories) {
			foreach($categories as $category) {
				$categoryModel = Category::FirstOrCreateUniqueSlug(['name' => $category]);
				$this->categories()->attach($categoryModel);
			}
		}
	}

	/**
	 * Define Runner many-to-many relationship.
	 *
	 * @return \Illuminate\Database\Eloquent\Relations\BelongsToMany
	 */
	public function runners() {
		return $this->belongsToMany('App\Runner');
	}

	/**
	 * Define Category many-to-many relationship.
	 *
	 * @return \Illuminate\Database\Eloquent\Relations\BelongsToMany
	 */
	public function categories() {
		return $this->belongsToMany('App\Category');
	}

	/**
	 * Define Event one-to-many relationship.
	 *
	 * @return \Illuminate\Database\Eloquent\Relations\BelongsTo
	 */
	public function event() {
		return $this->belongsTo('App\Event');
	}

	/**
	 * Define Platform one-to-many relationship.
	 *
	 * @return \Illuminate\Database\Eloquent\Relations\BelongsTo
	 */
	public function platform() {
		return $this->belongsTo('App\Platform');
	}

	/**
	 * Define Game one-to-many relationship.
	 *
	 * @return \Illuminate\Database\Eloquent\Relations\BelongsTo
	 */
	public function game() {
		return $this->belongsTo('App\Game');
	}

	protected $fillable = ['time', 'twitch_vod_id', 'youtube_vod_id', 'event_id', 'platform_id', 'game_id'];

}
