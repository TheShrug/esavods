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

Route::get('/dashboard/', 'DashboardController@index')->middleware('auth');
Route::post('/dashboard/run', 'DashboardController@addOrUpdateRun')->middleware('auth');

Route::post('/dashboard/category', 'DashboardController@addCategory')->middleware('auth');
Route::post('/dashboard/category/edit', 'DashboardController@editCategory')->middleware('auth');
Route::get('/dashboard/category', 'DashboardController@getCategories')->middleware('auth');



Route::get('/dashboard/all', 'DashboardController@getJson')->middleware('auth');