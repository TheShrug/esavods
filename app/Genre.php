<?php

namespace App;

use Illuminate\Database\Eloquent\Model;
use App\Traits\FirstOrCreateUniqueSlugTrait;

/**
 * App\Genre
 *
 * @property int $id
 * @property string $name
 * @property string|null $slug
 * @property string|null $description
 * @property \Illuminate\Support\Carbon|null $created_at
 * @property \Illuminate\Support\Carbon|null $updated_at
 * @property-read \Illuminate\Database\Eloquent\Collection|\App\Run[] $runs
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Genre whereCreatedAt($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Genre whereDescription($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Genre whereId($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Genre whereName($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Genre whereSlug($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Genre whereUpdatedAt($value)
 * @mixin \Eloquent
 */
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
