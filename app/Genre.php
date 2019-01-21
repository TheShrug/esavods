<?php

namespace App;

use Illuminate\Database\Eloquent\Model;
use App\Traits\FirstOrCreateUniqueSlugTrait;

class Genre extends Model
{
	use FirstOrCreateUniqueSlugTrait;

	/**
	 * Define Run many-to-many relationship.
	 *
	 * @return \Illuminate\Database\Eloquent\Relations\BelongsToMany
	 */
	public function runs() {
		return $this->belongsToMany('App\Run');
	}

	/**
	 * Override model method to make sure we detatch run if the category is deleted
	 *
	 * @return bool|null
	 * @throws \Exception
	 */
	public function delete() {
		$this->runs()->detach();

		return parent::delete();
	}

	protected $fillable = ['name', 'slug', 'description'];
}
