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

Route::get('/run/{id}', 'RunController@run');

Route::get('/event/', 'EventController@index');
Route::get('/event/{id}', 'EventController@event');

Route::get('/platform/', 'PlatformController@index');
Route::get('/platform/{id}', 'PlatformController@platform');

Route::get('/runner/{id}', 'RunnerController@runner');

Route::get('/category/', 'CategoryController@index');
Route::get('/category/{id}', 'CategoryController@category');

// Dashboard
Route::get('/dashboard/', 'DashboardController@index')->middleware('auth');
Route::get('/dashboard/all', 'DashboardController@getJson')->middleware('auth');

// Runs
Route::post('/dashboard/run', 'DashboardController@addOrUpdateRun')->middleware('auth');

// Categories
Route::post('/dashboard/category', 'DashboardController@addCategory')->middleware('auth');
Route::post('/dashboard/category/edit', 'DashboardController@editCategory')->middleware('auth');
Route::get('/dashboard/category', 'DashboardController@getCategories')->middleware('auth');

// Events
Route::post('/dashboard/event', 'DashboardController@addEvent')->middleware('auth');
Route::post('/dashboard/event/edit', 'DashboardController@editEvent')->middleware('auth');
Route::get('/dashboard/event', 'DashboardController@getEvents')->middleware('auth');

// Platforms
Route::post('/dashboard/platform', 'DashboardController@addPlatform')->middleware('auth');
Route::post('/dashboard/platform/edit', 'DashboardController@editPlatform')->middleware('auth');
Route::get('/dashboard/platform', 'DashboardController@getPlatforms')->middleware('auth');

// Games
Route::post('/dashboard/game', 'DashboardController@addGame')->middleware('auth');
Route::post('/dashboard/game/edit', 'DashboardController@editGame')->middleware('auth');
Route::get('/dashboard/game', 'DashboardController@getGames')->middleware('auth');



