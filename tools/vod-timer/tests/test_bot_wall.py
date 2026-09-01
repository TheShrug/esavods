"""Recognising YouTube's bot wall, so a blocked batch stops instead of grinding.

The strings here are the ones yt-dlp really emitted during the ESA Summer 2025
read, curly apostrophe included - that character is why the pattern matches on
"not a bot" rather than the whole sentence.

Run with:  python -m unittest discover -s tools/vod-timer/tests
"""
import unittest

from vodtimer.cli import _bot_walled

REAL = ("yt-dlp failed (1):\n  ERROR: [youtube] GF5eNjoyazM: Sign in to confirm "
        "you\u2019re not a bot. Use --cookies-from-browser or --cookies for the "
        "authentication.")


class RecognisesTheWall(unittest.TestCase):
    def test_the_message_we_actually_got(self):
        self.assertTrue(_bot_walled({"error": REAL}))

    def test_rate_limit_counts_too(self):
        self.assertTrue(_bot_walled({"error": "HTTP Error 429: Too Many Requests"}))


class LeavesEverythingElseAlone(unittest.TestCase):
    def test_a_successful_read_is_not_the_wall(self):
        self.assertFalse(_bot_walled({"confidence": "high", "final_time": "0:44:42"}))

    def test_a_broken_download_is_not_the_wall(self):
        """This one matters: ffmpeg failing means YouTube did answer us, so it
        resets the counter rather than advancing it."""
        self.assertFalse(_bot_walled(
            {"error": "ffmpeg failed (183): moov atom not found"}))

    def test_a_removed_video_is_not_the_wall(self):
        self.assertFalse(_bot_walled(
            {"error": "abc: no duration in metadata (members-only, or removed?)"}))

    def test_no_error_at_all(self):
        self.assertFalse(_bot_walled({}))


if __name__ == "__main__":
    unittest.main()
