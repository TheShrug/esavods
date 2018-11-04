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
 */
class Run extends Model
{

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
