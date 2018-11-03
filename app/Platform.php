<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Platform extends Model
{

	/**
	 * Define Run one-to-many relationship.
	 *
	 * @return \Illuminate\Database\Eloquent\Relations\HasMany
	 */
    public function runs() {
    	return $this->hasMany('App\Run');
    }

}
