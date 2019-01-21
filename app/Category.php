<?php

namespace App;

use Illuminate\Database\Eloquent\Model;
use App\Traits\FirstOrCreateUniqueSlugTrait;

/**
 * App\Category
 *
 * @property-read \Illuminate\Database\Eloquent\Collection|\App\Run[] $runs
 * @mixin \Eloquent
 * @property int $id
 * @property string $name
 * @property \Illuminate\Support\Carbon|null $created_at
 * @property \Illuminate\Support\Carbon|null $updated_at
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Category whereCreatedAt($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Category whereId($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Category whereName($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Category whereUpdatedAt($value)
 * @property string|null $slug
 * @property string|null $description
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Category whereDescription($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Category whereSlug($value)
 */
class Category extends Model
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
