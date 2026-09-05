<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * Drop events.year and events.order.
 *
 * Both were added in 2019 and set by hand; nothing has ever written them
 * programmatically, so every event the importer has created since carried
 * NULL in both. The menu ordered by them, which is why the whole 2021-2026
 * backfill sorted below ESA 2012 (#98). The order now derives from
 * MIN(runs.run_date), and no reader of either column is left — they were not
 * in Event::$fillable either, so nothing can even write them by accident.
 *
 * Dropping them loses the 21 hand-entered years. That is the point: a column
 * a person has to remember to fill in is the fault being fixed, and the dates
 * that replace it are already in the runs table.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::table('events', function (Blueprint $table) {
            $table->dropColumn(['year', 'order']);
        });
    }

    public function down(): void
    {
        Schema::table('events', function (Blueprint $table) {
            // Nullable, as they were. The values themselves are not recoverable
            // from here; the ordering no longer needs them.
            $table->integer('year')->nullable();
            $table->integer('order')->nullable();
        });
    }
};
