<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

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

}
