<?php

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| contains the "web" middleware group. Now create something great!
|
*/

Route::get('/', function () {
    return view('welcome');
});

Auth::routes();

Route::get('/', 'HomeController@index')->name('home');
Route::get('/about', 'HomeController@about')->name('about');

Route::get('/run/{id}', 'RunController@run');

Route::get('/event/', 'EventController@index');
Route::get('/event/{slug}', 'EventController@event')->name('event.show');

Route::get('/platform/', 'PlatformController@index');
Route::get('/platform/{slug}', 'PlatformController@platform')->name('platform.show');

Route::get('/runner/{slug}', 'RunnerController@runner')->name('runner.show');

Route::get('/category/', 'CategoryController@index');
Route::get('/category/{slug}', 'CategoryController@category')->name('category.show');

Route::get('/genre/', 'GenreController@index');
Route::get('/genre/{slug}', 'GenreController@genre')->name('genre.show');

Route::get('/game/', 'GameControler@index');
Route::get('/game/{slug}', 'GameController@game')->name('game.show');

// Dashboard
Route::get('/dashboard/', 'DashboardController@index')->middleware('auth');
Route::get('/dashboard/all', 'DashboardController@getJson')->middleware('auth');

// Runs
Route::post('/dashboard/run', 'DashboardController@addOrUpdateRun')->middleware('auth');
Route::post('/dashboard/run/edit', 'DashboardController@editRun')->middleware('auth');
Route::delete('/dashboard/run/{id}', 'DashboardController@deleteRun')->middleware('auth');

// Categories
Route::post('/dashboard/category', 'DashboardController@addCategory')->middleware('auth');
Route::post('/dashboard/category/edit', 'DashboardController@editCategory')->middleware('auth');
Route::get('/dashboard/category', 'DashboardController@getCategories')->middleware('auth');
Route::delete('/dashboard/category/{id}', 'DashboardController@deleteCategory')->middleware('auth');

// Genres
Route::post('/dashboard/genre', 'DashboardController@addGenre')->middleware('auth');
Route::post('/dashboard/genre/edit', 'DashboardController@editGenre')->middleware('auth');
Route::get('/dashboard/genre', 'DashboardController@getGenres')->middleware('auth');
Route::delete('/dashboard/genre/{id}', 'DashboardController@deleteGenre')->middleware('auth');

// Events
Route::post('/dashboard/event', 'DashboardController@addEvent')->middleware('auth');
Route::post('/dashboard/event/edit', 'DashboardController@editEvent')->middleware('auth');
Route::get('/dashboard/event', 'DashboardController@getEvents')->middleware('auth');
Route::delete('/dashboard/event/{id}', 'DashboardController@deleteEvent')->middleware('auth');

// Platforms
Route::post('/dashboard/platform', 'DashboardController@addPlatform')->middleware('auth');
Route::post('/dashboard/platform/edit', 'DashboardController@editPlatform')->middleware('auth');
Route::get('/dashboard/platform', 'DashboardController@getPlatforms')->middleware('auth');
Route::delete('/dashboard/platform/{id}', 'DashboardController@deletePlatform')->middleware('auth');

// Games
Route::post('/dashboard/game', 'DashboardController@addGame')->middleware('auth');
Route::post('/dashboard/game/edit', 'DashboardController@editGame')->middleware('auth');
Route::get('/dashboard/game', 'DashboardController@getGames')->middleware('auth');
Route::delete('/dashboard/game/{id}', 'DashboardController@deleteGame')->middleware('auth');

// Runners
Route::post('/dashboard/runner', 'DashboardController@addRunner')->middleware('auth');
Route::post('/dashboard/runner/edit', 'DashboardController@editRunner')->middleware('auth');
Route::get('/dashboard/runner', 'DashboardController@getRunners')->middleware('auth');
Route::delete('/dashboard/runner/{id}', 'DashboardController@deleteRunner')->middleware('auth');


