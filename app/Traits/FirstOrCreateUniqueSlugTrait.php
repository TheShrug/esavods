<?php

namespace App\Traits;

use App\Services\Slug;

trait FirstOrCreateUniqueSlugTrait
{

	/**
	 * @param array $firstOrCreateArray
	 *
	 * @return mixed
	 */
	public static function FirstOrCreateUniqueSlug(array $firstOrCreateArray) {
		$model = self::FirstOrCreate($firstOrCreateArray);
		if(empty($model->slug)) {
			$model->slug = Slug::createSlug($model['name'], $model);
			$model->save();
		}
		return $model;
	}

}