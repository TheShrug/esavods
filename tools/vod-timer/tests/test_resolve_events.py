"""Both backfilled events, resolved against a recorded candidate set.

Checking a change to `match()` against a real event costs one `ytsearch` per
run - 266 yt-dlp invocations for these two, and roughly 250 is what raised
YouTube's bot wall twice during ESA Summer 2025. One `ytsearch400:#<tag>`
returns the same videos in a single request, so `fixtures/*-vods.csv` holds
every candidate either event can offer and this runs offline, for ever, for
nothing.

It is a harder set to rank than the live search's, not an easier one: the
whole 400 results are handed to the ranker at once, decoys and neighbouring
years included, where `ytsearch6:<game> #<tag>` would have filtered most of
them out first. What it cannot show is a run whose video the recorded 400 do
not contain; those are the `weak` rows in the expected files, and `weak` has
meant "no video" on both of these events.

Run with:  python -m unittest discover -s tools/vod-timer/tests
"""
import csv
import json
import unittest
from importlib.resources import files

from vodtimer import resolve

EVENTS = {"esa-summer-2024": ("2024-summer", "ESASummer24"),
          "esa-winter-2021": ("2021-winter", "ESAWinter21")}


def fixture(name):
    return files("vodtimer.fixtures").joinpath(name).read_text(encoding="utf8")


def rows_of(event):
    slug = EVENTS[event][0]
    return resolve.schedule_rows(json.loads(fixture(f"{event}-schedule.json")), slug)


def vods_of(event):
    text = fixture(f"{event}-vods.csv")
    return [{"video_id": r["video_id"], "title": r["title"],
             "duration": int(r["duration"] or 0)}
            for r in csv.DictReader(
                l for l in text.splitlines() if not l.startswith("#"))]


def expected_of(event):
    text = fixture(f"{event}-resolved.csv")
    return list(csv.DictReader(
        l for l in text.splitlines() if not l.startswith("#")))


class EveryRunResolvesToTheSameVideoAsBefore(unittest.TestCase):
    def check(self, event):
        tag = EVENTS[event][1]
        vods = vods_of(event)
        want = {e["uuid"]: e for e in expected_of(event)}
        rows = rows_of(event)
        self.assertEqual(len(rows), len(want))
        for row in rows:
            e = want[row["UUID"]]
            best = resolve.best_of(row, tag, vods)
            with self.subTest(game=e["game"], category=e["category"]):
                self.assertEqual(best["video_id"], e["video_id"])
                self.assertEqual(resolve.verdict(best).split("(")[0], e["tier"])

    def test_esa_summer_2024(self):
        self.check("esa-summer-2024")

    def test_esa_winter_2021(self):
        self.check("esa-winter-2021")


class EveryVideoTheRecordedSetHoldsIsFound(unittest.TestCase):
    """Acceptance criterion 3, as far as an offline set can carry it.

    A run reported as having no video is the failure this ticket is about, so
    the assertion is on the bottom tier rather than on the top one: nothing
    may come back `no-hits`, and nothing may fall to `weak` that the recorded
    400 actually contain.
    """

    def check(self, event, weak_rows):
        tag = EVENTS[event][1]
        vods = vods_of(event)
        tiers = [resolve.verdict(resolve.best_of(r, tag, vods)).split("(")[0]
                 for r in rows_of(event)]
        self.assertEqual(tiers.count("no-hits"), 0)
        self.assertEqual(tiers.count("weak"), weak_rows)

    def test_esa_summer_2024(self):
        """24: seven `End of day N` filler rows, and 17 runs whose video the
        recorded 400 do not reach. Every one of the 17 was checked by hand."""
        self.check("esa-summer-2024", 24)

    def test_esa_winter_2021(self):
        """11, on the same footing - and one of them, Harry Potter and the
        Prisoner of Azkaban, has a video that carries no hashtag at all."""
        self.check("esa-winter-2021", 11)


class TheRunsThisTicketWasFiledFor(unittest.TestCase):
    """The named cases, resolved out of the whole recorded set."""

    def pick(self, event, game):
        tag = EVENTS[event][1]
        vods = vods_of(event)
        row = next(r for r in rows_of(event) if r["GameName"] == game)
        best = resolve.best_of(row, tag, vods)
        return best["video_id"], resolve.verdict(best).split("(")[0]

    def test_the_run_the_issue_quotes(self):
        """`Ratchet & Clank: Into The Nexus Syn #ESASummer24` found nothing."""
        self.assertEqual(self.pick("esa-summer-2024",
                                   "Ratchet & Clank: Into The Nexus"),
                         ("J6KShJ5Iofs", "tag-game-runner"))

    def test_the_other_ratchet_and_clank_is_not_confused_with_it(self):
        """Two games in one event, one name a prefix of the other."""
        self.assertEqual(self.pick("esa-summer-2024", "Ratchet & Clank"),
                         ("udq4sqL17p0", "tag-game-runner"))

    def test_the_two_stream_game_cell(self):
        """Its game name was `...Beta Quest + Stream 2` and matched nothing."""
        self.assertEqual(
            self.pick("esa-summer-2024",
                      "The Legend of Zelda Ocarina of Time Beta Quest"),
            ("MV-2HflPXKs", "tag-game-runner"))

    def test_the_title_with_no_bracket(self):
        """Mega Man 5's video used to win this row."""
        self.assertEqual(self.pick("esa-summer-2024", "Mega Man 2"),
                         ("ihKfreAoBso", "tag-game"))

    def test_winter_2021s_only_run_with_no_video(self):
        r"""The schedule spells the runner `C\_DOS\_KEZ`; the title, `CDOSKEZ`.

        This was the 1 `no-hits` in that event's 142, and the video was there
        the whole time.
        """
        self.assertEqual(self.pick("esa-winter-2021", "Metal Gear Ghost Babel"),
                         ("g2p1L9okYaQ", "tag-game"))


class TwoRunsOfOneGameStaySeparate(unittest.TestCase):
    """The risk in ranking on the runner instead of filtering on it.

    Both real pairs, scored with the schedule's runner names replaced by one
    no title carries - the shape of the six disagreements that started this.
    The `[Category]` bracket has to separate them unaided.
    """

    PAIRS = [("esa-summer-2024", "Sonic Adventure DX: Director's Cut"),
             ("esa-winter-2021", "Super Mario 64"),
             ("esa-winter-2021", "Fallout 3")]

    def test_each_pair_takes_its_own_video(self):
        for event, game in self.PAIRS:
            tag = EVENTS[event][1]
            vods = vods_of(event)
            want = {e["category"]: e["video_id"]
                    for e in expected_of(event) if e["game"] == game}
            self.assertEqual(len(want), 2, game)
            for row in rows_of(event):
                if row["GameName"] != game:
                    continue
                blind = dict(row, PlayerNamesTwitch='{"notthename": ""}')
                with self.subTest(game=game, category=row["CategoryName"]):
                    self.assertEqual(resolve.best_of(blind, tag, vods)["video_id"],
                                     want[row["CategoryName"]])


class BothRunnersOfARaceReachTheRanker(unittest.TestCase):
    """Real `A vs. B` rows out of the two schedules.

    ESA publishes one video per runner for a race, so which of the two the row
    ends up on turns on both names being available to rank with. Splitting the
    Player(s) cell on its comma alone left them as the single string
    `snee vs. xem92`, which confirms nothing.
    """

    RACES = [("esa-summer-2024", "Ratchet & Clank", ["snee", "xem92"]),
             ("esa-summer-2024", "The Legend of Zelda Ocarina of Time Beta Quest",
              ["Baal", "Runnerguy2489"]),
             ("esa-summer-2024", "Pokémon Platinum", ["marchspec", "Rubentus"]),
             ("esa-winter-2021", "The Legend of Zelda: Link's Awakening (2019)",
              ["Strackel", "Miniretin"]),
             ("esa-winter-2021", "SegaSonic the Hedgehog",
              ["Hibnotix", "STwoLive"])]

    def test_every_name_is_its_own_runner(self):
        for event, game, want in self.RACES:
            row = next(r for r in rows_of(event) if r["GameName"] == game)
            with self.subTest(event=event, game=game):
                self.assertEqual(resolve.players(row["PlayerNamesTwitch"]), want)

    def test_the_second_name_is_the_one_that_confirms_the_match(self):
        """Pokémon Platinum's title names `linewashere and Rubentus`.

        The schedule's first runner is `marchspec`, who is in no title on the
        event. Keeping only the first name left this a `tag-game` match.
        """
        event, game = "esa-summer-2024", "Pokémon Platinum"
        row = next(r for r in rows_of(event) if r["GameName"] == game)
        best = resolve.best_of(row, EVENTS[event][1], vods_of(event))
        self.assertTrue(best["runner"])
        self.assertTrue(resolve.verdict(best).startswith("tag-game-runner("))

    def test_a_race_with_a_video_each_still_lands_where_it_shipped(self):
        """One schedule row, two runners, and ESA published a VOD for each.

        #45 flagged which of the two the row should carry as a call for a
        person; the row names both runners, so both videos now confirm on the
        runner and neither name breaks the tie. This pins the choice against
        the one that shipped rather than claiming the tool made it.
        """
        event = "esa-summer-2024"
        row = next(r for r in rows_of(event)
                   if r["GameName"] == "The Legend of Zelda Ocarina of Time Beta Quest")
        best = resolve.best_of(row, EVENTS[event][1], vods_of(event))
        self.assertIn("BaalNocturno", best["title"])
        self.assertEqual(best["video_id"], "MV-2HflPXKs")


if __name__ == "__main__":
    unittest.main()
