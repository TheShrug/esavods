<?php

use App\WatchedRun;
use Illuminate\Database\Migrations\Migration;

/**
 * Retire the watches recorded before the #31 backfill, so the homepage's
 * most-watched list reflects the site as it is now.
 *
 * The counts being cleared were accumulated when the site held twelve fewer
 * years of events. Left alone they would keep the same handful of runs pinned
 * to the front page indefinitely, because a run listed since 2019 outpolls one
 * added last week no matter how good it is.
 *
 * **The cutoff is the epic, not "everything".** Epic #31 was opened
 * 2026-08-23 and the first backfilled event merged a week later, so every
 * watch since then was cast against a site that already had new events on it.
 * Those are real signal about the new material and are kept.
 *
 * `old` is the mechanism and it already exists: added in 2019
 * (`2019_07_29_012931_add_old_to_watched_runs_table`), and
 * `WatchedRun::getTopWatchedRunIds()` filters `where('old', '=', 0)`. Flagging
 * a row removes it from the ranking while keeping it on disk. Nothing is
 * deleted here.
 */
return new class extends Migration
{
    /**
     * Midnight UTC on the day epic #31 was opened.
     *
     * A date rather than the issue's exact timestamp (15:32:11Z): the boundary
     * only has to separate "before the backfill" from "during it", and a whole
     * day is easier to check against the database by hand than a time is.
     */
    private const EPIC_STARTED = '2026-08-23 00:00:00';

    public function up(): void
    {
        WatchedRun::retireWatchesBefore(self::EPIC_STARTED);
    }

    /**
     * Deliberately does nothing.
     *
     * Reversing this would mean clearing `old` on every row it touched - but
     * the column was already in use before this migration, so a blanket clear
     * would also un-retire whatever the 2019 reset flagged, and the ids this
     * migration was responsible for are not recorded anywhere. A rollback that
     * silently resurrects an older reset is worse than one that does nothing.
     */
    public function down(): void
    {
        //
    }
};
