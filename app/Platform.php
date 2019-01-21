<?php

namespace App;

use Illuminate\Database\Eloquent\Model;
use App\Traits\FirstOrCreateUniqueSlugTrait;

/**
 * App\Platform
 *
 * @property-read \Illuminate\Database\Eloquent\Collection|\App\Run[] $runs
 * @mixin \Eloquent
 * @property int $id
 * @property string $name
 * @property \Illuminate\Support\Carbon|null $created_at
 * @property \Illuminate\Support\Carbon|null $updated_at
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Platform whereCreatedAt($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Platform whereId($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Platform whereName($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Platform whereUpdatedAt($value)
 * @property string|null $slug
 * @property string|null $description
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Platform whereDescription($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Platform whereSlug($value)
 */
class Platform extends Model
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
