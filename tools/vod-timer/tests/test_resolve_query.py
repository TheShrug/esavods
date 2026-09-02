"""The runner ranks a candidate; it never decides which candidates exist.

`match()` used to search for game + runner + tag. YouTube's search is
conjunctive enough that one token nothing matches returns no results at all
rather than worse ones, and horaro's Player(s) cell is under no obligation to
agree with a VOD title about a runner's name - ESA Summer 2024's schedule
holds Oengus display names where the titles hold Twitch handles. Six such
disagreements cost that event 14 of its 124 runs, each reported as a video
that does not exist. So the query is game + tag, and the runner earns a place
in rank() instead.

Run with:  python -m unittest discover -s tools/vod-timer/tests
"""
import unittest

from vodtimer import resolve

TAG = "ESASummer24"

# horaro's name against ESA's, for the six ESA Summer 2024 runs where the two
# disagree. Every one of these came back `no-hits` with the left-hand name in
# the query, and resolved on `<game> #<tag>` alone once it was out.
DISAGREED = [("Syn", "synn1_"), ("Bassguy", "bassguy4"), ("Zyper", "Zyper_S"),
             ("Nitroz", "NitrozSR"), ("prisi", "prisiii3"), ("lurven", "lurven_")]


def row(game, category="Any%", *runners):
    return {"GameName": game, "CategoryName": category,
            "PlayerNamesTwitch": '{%s}' % ", ".join('"%s": ""' % r for r in runners),
            "_slot": None}


def hit(video_id, title, duration=3600):
    return {"video_id": video_id, "title": title, "duration": duration}


class TheQuery(unittest.TestCase):
    def test_is_the_game_and_the_tag(self):
        self.assertEqual(
            resolve.search_query(row("Super Metroid", "Any%", "Behemoth87"), TAG),
            "Super Metroid #ESASummer24")

    def test_never_carries_a_runner(self):
        for horaro, _ in DISAGREED:
            q = resolve.search_query(row("Ratchet & Clank: Into The Nexus",
                                         "NG+", horaro), TAG)
            self.assertNotIn(horaro.lower(), q.lower())


class ADisagreedNameCostsAPlaceAndNotTheRun(unittest.TestCase):
    """The run the issue quotes: `Syn` in the schedule, `synn1_` in the title.

    Note what the runner check makes of that once the video is in front of it:
    `syn` is a substring of `synn1_`, so the match is confirmed on the runner
    as well. All six of the disagreed names are prefixes of the handle. None
    of that ever got a chance to run, because the search had already returned
    nothing - which is the whole of the bug.
    """

    ROW = row("Ratchet & Clank: Into The Nexus", "NG+", "Syn")
    REAL = hit("J6KShJ5Iofs",
               "Ratchet & Clank: Into The Nexus [NG+] by synn1_ - #ESASummer24")

    def test_the_video_is_found(self):
        best = resolve.best_of(self.ROW, TAG, [self.REAL])
        self.assertEqual(best["video_id"], "J6KShJ5Iofs")
        self.assertTrue(resolve.verdict(best).startswith("tag-game-runner("))

    def test_a_name_that_does_not_agree_at_all_only_costs_the_confirmation(self):
        r"""ESA Winter 2021 spells one runner `C\_DOS\_KEZ` against `CDOSKEZ`.

        That was the event's only `no-hits`. It should be a match reported
        one tier down, not a video declared not to exist.
        """
        r = row("Metal Gear Ghost Babel", "Any% (Easy)", r"C\_DOS\_KEZ")
        real = hit("g2p1L9okYaQ",
                   "Metal Gear Ghost Babel [Any% (Easy)] by CDOSKEZ - #ESAWinter21")
        best = resolve.best_of(r, "ESAWinter21", [real])
        self.assertEqual(best["video_id"], "g2p1L9okYaQ")
        self.assertFalse(best["runner"])
        self.assertTrue(resolve.verdict(best).startswith("tag-game("))


class TheRunnerRanksBelowTheGame(unittest.TestCase):
    """A runner's name in an unrelated title is a coincidence.

    With the runner gone from the query the candidate set is chosen on game
    and tag, so these decoys are in it - and while `runner` sorted above the
    game they won. Both of these are real ESA Winter 2021 / Summer 2024 pairs.
    """

    def test_the_right_game_beats_a_shared_runner_name(self):
        turtles = row("Teenage Mutant Ninja Turtles: Out of the Shadows",
                      "NG+ (Co-op)", "havrd", "Kainalo")
        hits = [hit("rVJbJAxJE-c", "Baby Shark VR Dancing [Any%] by Kainalo - #ESAWinter21"),
                hit("8-nL77Ty-wE", "Teenage Mutant Ninja Turtles: Out of the "
                                   "Shadows [NG+ (Co-op)] - #ESAWinter21")]
        best = resolve.best_of(turtles, "ESAWinter21", hits)
        self.assertEqual(best["video_id"], "8-nL77Ty-wE")

    def test_but_it_still_separates_two_runs_of_one_game(self):
        hits = [hit("C2-04i_zt9k", "Sonic Adventure DX: Director's Cut "
                                   "[Sonic's Story] by DreeGon - #ESASummer24"),
                hit("yjTySRhIQz0", "Sonic Adventure DX: Director's Cut "
                                   "[Amy's Story] by ChZdk - #ESASummer24")]
        amy = row("Sonic Adventure DX: Director's Cut", "Amy's Story", "ChZdk")
        self.assertEqual(resolve.best_of(amy, TAG, hits)["video_id"], "yjTySRhIQz0")


class TheBracketDoesTheJobWhenTheRunnerCannot(unittest.TestCase):
    """Acceptance criterion 2, on the pair the runner used to separate.

    The same two videos, with the schedule naming a runner neither title
    carries - which is exactly the shape of the six disagreements above. The
    `[Category]` bracket has to be enough on its own.
    """

    HITS = [hit("C2-04i_zt9k", "Sonic Adventure DX: Director's Cut "
                               "[Sonic's Story] by DreeGon - #ESASummer24"),
            hit("yjTySRhIQz0", "Sonic Adventure DX: Director's Cut "
                               "[Amy's Story] by ChZdk - #ESASummer24")]

    def test_sonics_story(self):
        r = row("Sonic Adventure DX: Director's Cut", "Sonic's Story", "notthename")
        self.assertEqual(resolve.best_of(r, TAG, self.HITS)["video_id"], "C2-04i_zt9k")

    def test_amys_story(self):
        r = row("Sonic Adventure DX: Director's Cut", "Amy's Story", "notthename")
        self.assertEqual(resolve.best_of(r, TAG, self.HITS)["video_id"], "yjTySRhIQz0")


if __name__ == "__main__":
    unittest.main()
