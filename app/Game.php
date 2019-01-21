<?php

namespace App;

use Illuminate\Database\Eloquent\Model;
use App\Traits\FirstOrCreateUniqueSlugTrait;

/**
 * App\Game
 *
 * @property-read \Illuminate\Database\Eloquent\Collection|\App\Run[] $runs
 * @mixin \Eloquent
 * @property int $id
 * @property string $name
 * @property \Illuminate\Support\Carbon|null $created_at
 * @property \Illuminate\Support\Carbon|null $updated_at
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Game whereCreatedAt($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Game whereId($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Game whereName($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Game whereUpdatedAt($value)
 * @property string|null $slug
 * @property string|null $description
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Game whereDescription($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Game whereSlug($value)
 */
class Game extends Model
{
	use FirstOrCreateUniqueSlugTrait;

	/**
	 * Define Run one-to-many relationship.
	 *
	 * @return \Illuminate\Database\Eloquent\Relations\HasMany
	 */
    public function runs() {
    	return $this->hasMany('App\Run');
    }

	protected $fillable = ['name', 'slug', 'description'];
}
