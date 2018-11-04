<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

/**
 * App\Event
 *
 * @property-read \Illuminate\Database\Eloquent\Collection|\App\Run[] $runs
 * @mixin \Eloquent
 * @property int $id
 * @property string $name
 * @property \Illuminate\Support\Carbon|null $created_at
 * @property \Illuminate\Support\Carbon|null $updated_at
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Event whereCreatedAt($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Event whereId($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Event whereName($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Event whereUpdatedAt($value)
 */
class Event extends Model
{

	/**
	 * Define Run one-to-many relationship.
	 *
	 * @return \Illuminate\Database\Eloquent\Relations\HasMany
	 */
    public function runs() {
    	return $this->hasMany('App\Run');
    }

	protected $fillable = ['name'];

}
