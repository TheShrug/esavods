"""Reading a VOD title that does not follow ESA's own convention.

ESA titles a per-run VOD `Game [Category] by Runner - #tag`, and both halves
of the scoring assumed it: the game was whatever came before ` [`, and the
category was whatever was inside the first bracket or nothing at all. ESA
Summer 2024 broke that twice in one event - `Mega Man 2 Relay Race (any%) -
#ESASummer24` names its category in parentheses and no runner, and scored
zero for category against the Mega Man 2 row it belongs to.

Run with:  python -m unittest discover -s tools/vod-timer/tests
"""
import unittest

from vodtimer.resolve import gscore, title_fields


class SplitsATitle(unittest.TestCase):
    def test_the_convention(self):
        self.assertEqual(
            title_fields("Grand Theft Auto: San Andreas [Any% No Major Glitches] "
                         "by Joshimuz - #ESASummer24"),
            ("Grand Theft Auto: San Andreas", "Any% No Major Glitches"))

    def test_a_category_in_parentheses(self):
        self.assertEqual(title_fields("Mega Man 2 Relay Race (any%) - #ESASummer24"),
                         ("Mega Man 2 Relay Race", "any%"))

    def test_no_runner_named(self):
        self.assertEqual(title_fields("Flash Game Gauntlet [Any%?] - #ESASummer24"),
                         ("Flash Game Gauntlet", "Any%?"))

    def test_no_category_at_all(self):
        """The hashtag still has to come off, or it scores as part of the game."""
        self.assertEqual(
            title_fields("Bowser's Fury Speedrun by Samura1man - #ESAWinter21"),
            ("Bowser's Fury Speedrun by Samura1man", ""))

    def test_a_bracket_wins_over_a_by_in_the_game_name(self):
        self.assertEqual(
            title_fields("Kingdom Hearts Birth by Sleep Final Mix HD "
                         "[Ventus Critical Level 1 Any%] - #ESASummer24"),
            ("Kingdom Hearts Birth by Sleep Final Mix HD",
             "Ventus Critical Level 1 Any%"))


class ScoresTheGame(unittest.TestCase):
    def test_a_wrong_digit_is_a_different_game(self):
        """Mega Man 5's video outscored Mega Man 2's own on the Mega Man 2 row."""
        self.assertGreater(gscore("Mega Man 2", "Mega Man 2 Relay Race"),
                           gscore("Mega Man 2", "Mega Man 5"))

    def test_extra_words_are_cheaper_than_a_missing_one(self):
        self.assertGreater(gscore("Halo 3", "Halo 3: ODST"), gscore("Halo 3", "Halo 2"))

    def test_a_longer_title_is_still_not_the_short_one(self):
        """The other half of the same trade: `Portal` is not "Portal 2"."""
        self.assertGreater(gscore("Portal", "Portal"), gscore("Portal", "Portal 2"))
        self.assertGreater(gscore("Ratchet & Clank", "Ratchet & Clank"),
                           gscore("Ratchet & Clank", "Ratchet & Clank: Into The Nexus"))

    def test_a_word_said_twice_is_one_word(self):
        """`Yogho! Yogho!` scored 0.5 against its own video while it was two."""
        self.assertEqual(gscore("Yogho! Yogho!", "Yogho! Yogho!"), 1.0)

    def test_nothing_in_common_falls_back_to_the_spelling(self):
        self.assertGreater(gscore("Streemerz", "Streemer"), 0.75)
        self.assertEqual(gscore("Super Metroid", ""), 0.0)


if __name__ == "__main__":
    unittest.main()
