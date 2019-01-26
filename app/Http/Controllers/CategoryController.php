<?php

namespace App\Http\Controllers;

use App\Category;
use Illuminate\Http\Request;

class CategoryController extends Controller
{
	/**
	 * @param $slug
	 *
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */
	public function category($slug) {
		$category = Category::where('slug', '=', $slug)->firstOrFail();
		$runs = $category->runs;
		return view('category', [
			'runs' => $runs,
			'category' => $category
		]);
	}

	/**
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */
	public function index() {
		$categories = Category::get();
		return view('categoryIndex', [
			'categories' => $categories,
			'title' => 'Categories - All categories of speedruns at ESA Marathon Events',
			'description' => "Navigate through all the categories of speedruns at European Speedrunner Assembly's events and select VODs to watch."
		]);
	}
}
