<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

/**
 * App\Runner
 *
 * @property-read \Illuminate\Database\Eloquent\Collection|\App\Run[] $runs
 * @mixin \Eloquent
 * @property int $id
 * @property string $name
 * @property string|null $twitch
 * @property string|null $twitter
 * @property string|null $youtube
 * @property \Illuminate\Support\Carbon|null $created_at
 * @property \Illuminate\Support\Carbon|null $updated_at
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Runner whereCreatedAt($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Runner whereId($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Runner whereName($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Runner whereTwitch($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Runner whereTwitter($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Runner whereUpdatedAt($value)
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Runner whereYoutube($value)
 * @property string|null $slug
 * @method static \Illuminate\Database\Eloquent\Builder|\App\Runner whereSlug($value)
 */
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

	protected $fillable = ['name', 'twitch', 'twitter', 'youtube', 'slug'];
}
