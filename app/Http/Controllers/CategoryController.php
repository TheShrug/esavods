<?php

namespace App\Http\Controllers;

use App\Category;
use Illuminate\Http\Request;

class CategoryController extends Controller
{
	/**
	 * Return the view showcasing the runs belonging to the category of the slug provided
	 *
	 * @param $slug
	 *
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */
	public function category($slug) {
		$category = Category::where('slug', '=', $slug)->firstOrFail();
		$runs = $category->runs;
		$title = 'Commentated ' . $category->name . ' speedrun VODs - VODs by Category';
		$description = 'Archive of all European Speedrunner Assembly VODs in the ' . $category->name . ' category. ' . $category->description;
		return view('category', [
			'runs' => $runs,
			'category' => $category,
			'title' => $title,
			'description' => $description
		]);
	}

	/**
	 * Return the view with showcasing all of the categories on the site
	 *
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */
	public function index() {
		$categories = Category::withCount('runs')->get();
		return view('categoryIndex', [
			'categories' => $categories,
			'title' => 'Categories - All categories of speedruns at ESA Marathon Events',
			'description' => "Navigate through all the categories of speedruns at European Speedrunner Assembly's events and select VODs to watch."
		]);
	}
}
