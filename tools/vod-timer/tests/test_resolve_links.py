"""The schedule's own VOD link, where ESA publishes one.

From Summer 2025 the horaro schedule links each run to its video from the Game
cell. That is the organisers naming their own upload, so it is not a match to be
scored against a title search - it is the answer. These tests pin the two halves
of that: pulling the id out of the cell, and leaving every pre-2025 schedule,
which has no links at all, on the search path exactly as before.

Run with:  python -m unittest discover -s tools/vod-timer/tests
"""
import unittest

from vodtimer.resolve import YT_LINK, _names, _plain


class ExtractsTheId(unittest.TestCase):
    def id_in(self, cell):
        m = YT_LINK.search(cell)
        return m.group(1) if m else None

    def test_watch_url(self):
        cell = "[Jak and Daxter: The Precursor Legacy](https://www.youtube.com/watch?v=kt6YrQUNj8s)"
        self.assertEqual(self.id_in(cell), "kt6YrQUNj8s")

    def test_short_url(self):
        self.assertEqual(self.id_in("[Undertale](https://youtu.be/l01Pu8dOZTI)"),
                         "l01Pu8dOZTI")

    def test_ids_with_dash_and_underscore(self):
        """Both are legal in a video id and both appear in this event."""
        self.assertEqual(
            self.id_in("[Halo Infinite](https://www.youtube.com/watch?v=_scTYuGX7RU)"),
            "_scTYuGX7RU")
        self.assertEqual(
            self.id_in("[Metaphor](https://www.youtube.com/watch?v=Y_fGvAu33E4)"),
            "Y_fGvAu33E4")

    def test_takes_the_first_of_a_multi_part_run(self):
        """ESA splits a long run over several videos and links them all."""
        cell = ("[Final Fantasy IX](https://www.youtube.com/watch?v=AAAAAAAAAAA) - "
                "[Part 2](https://www.youtube.com/watch?v=BBBBBBBBBBB)")
        self.assertEqual(self.id_in(cell), "AAAAAAAAAAA")

    def test_a_second_stream_is_not_part_of_the_game_name(self):
        """ESA links both halves of a split run from the one Game cell.

        Keeping every link text made the game name `The Legend of Zelda
        Ocarina of Time Beta Quest + Stream 2`, which matched no VOD at all.
        """
        cell = ("[The Legend of Zelda Ocarina of Time Beta Quest]"
                "(https://www.twitch.tv/videos/2205517572) + "
                "[Stream 2](https://www.twitch.tv/videos/2205520740)")
        self.assertEqual(_plain(cell),
                         "The Legend of Zelda Ocarina of Time Beta Quest")

    def test_a_cell_with_no_link_is_its_own_text(self):
        self.assertEqual(_plain("Super Metroid"), "Super Metroid")

    def test_no_link_is_no_id(self):
        """Every schedule before Summer 2025 looks like this."""
        self.assertIsNone(self.id_in("Super Metroid"))
        self.assertIsNone(self.id_in("[Super Metroid](https://www.speedrun.com/smw)"))

    def test_game_name_still_loses_the_markdown(self):
        """The link is taken as well as, not instead of, the plain name."""
        cell = "[Astro Bot](https://www.youtube.com/watch?v=kt6YrQUNj8s)"
        self.assertEqual(_plain(cell), "Astro Bot")


class NamesEveryRunner(unittest.TestCase):
    """The Player(s) cell, where a second link means a second person.

    The Game cell and this one look alike and mean opposite things: a second
    link there is a second stream for one run, here it is another runner. ESA
    writes a race as one comma-part holding two links, so taking the first
    link would drop half the field, and taking the cell whole - which is what
    it used to do - yields `snee vs. xem92`, a name no title carries either.
    """

    def test_a_race_is_two_runners(self):
        cell = ("[snee](https://oengus.io/user/snee) vs. "
                "[xem92](https://oengus.io/user/xem92)")
        self.assertEqual(_names(cell), ["snee", "xem92"])

    def test_a_co_op_run_is_still_split_on_the_comma(self):
        cell = ("[Xita](https://www.twitch.tv/Xita), "
                "[Wiredwicky](https://www.twitch.tv/Wiredwicky)")
        self.assertEqual(_names(cell), ["Xita", "Wiredwicky"])

    def test_one_runner_is_one_name(self):
        self.assertEqual(_names("[Pengyy](https://www.twitch.tv/pengyy)"), ["Pengyy"])

    def test_a_name_with_no_link_is_kept_whole(self):
        """`Team 1 vs. Team 2` names nobody a title could confirm."""
        self.assertEqual(_names("Team 1 vs. Team 2"), ["Team 1 vs. Team 2"])
        self.assertEqual(_names("Halo 3 Relay Team"), ["Halo 3 Relay Team"])

    def test_an_empty_cell_names_nobody(self):
        self.assertEqual(_names(""), [])
        self.assertEqual(_names(None), [])


if __name__ == "__main__":
    unittest.main()
