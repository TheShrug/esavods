<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Runner extends Model
{

	/**
	 * Define Run many-to-many relationship.
	 *
	 * @return \Illuminate\Database\Eloquent\Relations\BelongsToMany
	 */
    public function runs() {
    	return $this->belongsToMany('App\Run');
    }
}
