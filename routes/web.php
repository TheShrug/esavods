<?php

use App\Http\Controllers\CategoryController;
use App\Http\Controllers\EventController;
use App\Http\Controllers\GameController;
use App\Http\Controllers\GenreController;
use App\Http\Controllers\HomeController;
use App\Http\Controllers\PlatformController;
use App\Http\Controllers\RunController;
use App\Http\Controllers\RunnerController;
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
