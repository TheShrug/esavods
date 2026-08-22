<?php

use App\Http\Controllers\CategoryController;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\EventController;
use App\Http\Controllers\GameController;
use App\Http\Controllers\GenreController;
use App\Http\Controllers\HomeController;
use App\Http\Controllers\PlatformController;
use App\Http\Controllers\RunController;
use App\Http\Controllers\RunnerController;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Route;

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

Auth::routes(['register' => false]);

// 301 redirects on top
Route::get('/event/esa-2019-one', function() {
	return redirect('/event/esa-2019-summer-one', 301);
});
Route::get('/event/esa-2019-two', function() {
	return redirect('/event/esa-2019-summer-two', 301);
});

Route::get('/event/esa-2018', function() {
	return redirect('/event/esa-2018-summer-one', 301);
});
Route::get('/event/esa-2018-two', function() {
	return redirect('/event/esa-2018-summer-two', 301);
});

Route::get('/platform/gp-player', function() {
	return redirect('/platform/game-boy', 301);
});
Route::get('/platform/gb', function() {
	return redirect('/platform/game-boy', 301);
});

Route::get('/platform/gameboy-player', function() {
	return redirect('/platform/game-boy', 301);
});
Route::get('/platform/gpp', function() {
	return redirect('/platform/game-boy', 301);
});
Route::get('/platform/gc', function() {
	return redirect('/platform/gamecube', 301);
});
Route::get('/platform/gcn', function() {
	return redirect('/platform/gamecube', 301);
});

Route::get('/platform/gba', function() {
	return redirect('/platform/game-boy-advance', 301);
});
Route::get('/platform/gba-emu', function() {
	return redirect('/platform/game-boy-advance', 301);
});
Route::get('/platform/gbs-emu', function() {
	return redirect('/platform/game-boy-advance', 301);
});





Route::get('/', [HomeController::class, 'index'])->name('home');
Route::get('/about', [HomeController::class, 'about'])->name('about');

Route::post('/run/{id}', [RunController::class, 'watchedRun']);

Route::get('/event/', [EventController::class, 'index'])->name('events');
Route::get('/event/{slug}', [EventController::class, 'event'])->name('event.show');

Route::get('/platform/', [PlatformController::class, 'index'])->name('platforms');
Route::get('/platform/{slug}', [PlatformController::class, 'platform'])->name('platform.show');

Route::get('/runner/{slug}', [RunnerController::class, 'runner'])->name('runner.show');

Route::get('/category/', [CategoryController::class, 'index'])->name('categories');
Route::get('/category/{slug}', [CategoryController::class, 'category'])->name('category.show');

Route::get('/genre/', [GenreController::class, 'index'])->name('genres');
Route::get('/genre/{slug}', [GenreController::class, 'genre'])->name('genre.show');

Route::get('/game/', [GameController::class, 'index'])->name('games');
Route::get('/game/{slug}', [GameController::class, 'game'])->name('game.show');




// Dashboard
Route::get('/dashboard/', [DashboardController::class, 'index'])->middleware('auth');
Route::get('/dashboard/all', [DashboardController::class, 'getJson'])->middleware('auth');
Route::get('/dashboard/runs', [DashboardController::class, 'getRunsJson'])->middleware('auth');

// Runs
Route::post('/dashboard/run', [DashboardController::class, 'addOrUpdateRun'])->middleware('auth');
Route::post('/dashboard/run/edit', [DashboardController::class, 'editRun'])->middleware('auth');
Route::post('/dashboard/runs/upload', [DashboardController::class, 'uploadCsv'])->middleware('auth');
Route::delete('/dashboard/run/{id}', [DashboardController::class, 'deleteRun'])->middleware('auth');

// Categories
Route::post('/dashboard/category', [DashboardController::class, 'addCategory'])->middleware('auth');
Route::post('/dashboard/category/edit', [DashboardController::class, 'editCategory'])->middleware('auth');
Route::get('/dashboard/category', [DashboardController::class, 'getCategories'])->middleware('auth');
Route::delete('/dashboard/category/{id}', [DashboardController::class, 'deleteCategory'])->middleware('auth');

// Genres
Route::post('/dashboard/genre', [DashboardController::class, 'addGenre'])->middleware('auth');
Route::post('/dashboard/genre/edit', [DashboardController::class, 'editGenre'])->middleware('auth');
Route::get('/dashboard/genre', [DashboardController::class, 'getGenres'])->middleware('auth');
Route::delete('/dashboard/genre/{id}', [DashboardController::class, 'deleteGenre'])->middleware('auth');

// Events
Route::post('/dashboard/event', [DashboardController::class, 'addEvent'])->middleware('auth');
Route::post('/dashboard/event/edit', [DashboardController::class, 'editEvent'])->middleware('auth');
Route::get('/dashboard/event', [DashboardController::class, 'getEvents'])->middleware('auth');
Route::delete('/dashboard/event/{id}', [DashboardController::class, 'deleteEvent'])->middleware('auth');

// Platforms
Route::post('/dashboard/platform', [DashboardController::class, 'addPlatform'])->middleware('auth');
Route::post('/dashboard/platform/edit', [DashboardController::class, 'editPlatform'])->middleware('auth');
Route::get('/dashboard/platform', [DashboardController::class, 'getPlatforms'])->middleware('auth');
Route::delete('/dashboard/platform/{id}', [DashboardController::class, 'deletePlatform'])->middleware('auth');

// Games
Route::post('/dashboard/game', [DashboardController::class, 'addGame'])->middleware('auth');
Route::post('/dashboard/game/edit', [DashboardController::class, 'editGame'])->middleware('auth');
Route::get('/dashboard/game', [DashboardController::class, 'getGames'])->middleware('auth');
Route::delete('/dashboard/game/{id}', [DashboardController::class, 'deleteGame'])->middleware('auth');

// Runners
Route::post('/dashboard/runner', [DashboardController::class, 'addRunner'])->middleware('auth');
Route::post('/dashboard/runner/edit', [DashboardController::class, 'editRunner'])->middleware('auth');
Route::get('/dashboard/runner', [DashboardController::class, 'getRunners'])->middleware('auth');
Route::delete('/dashboard/runner/{id}', [DashboardController::class, 'deleteRunner'])->middleware('auth');


