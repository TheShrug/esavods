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
	public static function FirstOrCreateUniqueSlug(array $firstOrCreateArray, array $fieldsToAdd = []) {
		$model = self::FirstOrCreate($firstOrCreateArray, $fieldsToAdd);
		if(empty($model->slug)) {
			$model->slug = Slug::createSlug($model['name'], $model);
			$model->save();
		}
		return $model;
	}

}