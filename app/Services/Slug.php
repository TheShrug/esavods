<?php

namespace App\Services;

use Illuminate\Database\Eloquent\Model;

class Slug
{

	/**
	 * @param $title
	 * @param Model $model
	 *
	 * @return string
	 */
	public static function createSlug($title, Model $model) {
		$slug = str_slug($title);
		$similarSlugs = self::findSimilarSlugs($slug, $model);

		if (!$similarSlugs->contains('slug', $slug)){
			return $slug;
		}

		for ($i = 1; $i <= 10; $i++) {
			$newSlug = $slug.'-'.$i;
			if (!$similarSlugs->contains('slug', $newSlug)) {
				return $newSlug;
			}
		}
	}

	/**
	 * @param $slug
	 * @param Model $model
	 *
	 * @return mixed
	 */
	protected static function findSimilarSlugs($slug, Model $model)
	{
		$query = $model::query();
		return $query->select('slug')->where('slug', 'like', $slug.'%')
		           ->where('id', '<>', $model->getQueueableId())
		           ->get();
	}

}