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
 * @property-read \Illuminate\Database\Eloquent\Collection|\App\Genre[] $genres
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

	public function addGenres(array $genres) {
		if($genres) {
			foreach($genres as $genre) {
				$genreModel = Genre::FirstOrCreateUniqueSlug(['name' => $genre]);
				$this->genres()->attach($genreModel);
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
	 * Define Genre many-to-many relationship.
	 *
	 * @return \Illuminate\Database\Eloquent\Relations\BelongsToMany
	 */
	public function genres() {
		return $this->belongsToMany('App\Genre');
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

	/**
	 * Override to make sure to detatch categories and runners
	 * so we don't end up with orphaned rows
	 *
	 * @return bool|null
	 * @throws \Exception
	 */
	public function delete() {
		$this->categories()->detach();
		$this->runners()->detach();

		return parent::delete();
	}

	protected $fillable = ['time', 'twitch_vod_id', 'youtube_vod_id', 'event_id', 'platform_id', 'game_id'];

}
