<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreateRunsTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('runs', function (Blueprint $table) {
            $table->increments('id');
	        $table->float('time',12,3);
	        $table->string('category')->nullable();
	        $table->string('twitch_vod_id')->nullable();
	        $table->string('youtube_vod_id')->nullable();
	        $table->integer('event_id')->nullable();
	        $table->integer('platform_id')->nullable();
	        $table->integer('game_id')->nullable();
	        $table->dateTime('run_date')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('runs');
    }
}
