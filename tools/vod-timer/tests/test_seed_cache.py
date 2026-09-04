"""Seeding the metadata cache from resolve's own search results.

The saving this buys is a yt-dlp request per run, on a wall that is counted in
requests: ESA Summer 2023 spent ~200 re-asking for a title and duration
`resolve` had already been told. Run with:

    python -m unittest discover -s tools/vod-timer/tests
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from vodtimer import video


class Seeding(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        patcher = mock.patch.dict("os.environ", {"VODTIMER_CACHE": self.tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.tmp.cleanup)

    def entry(self, vid):
        return json.loads((Path(self.tmp.name) / f"{vid}.meta.json").read_text())

    def test_a_seeded_entry_is_what_probe_reads_back(self):
        self.assertTrue(video.seed("abc12345678", "Hades [Dash Only] by OckE", 1489))
        meta = video.probe("abc12345678")     # no network: the cache answers
        self.assertEqual(meta.duration, 1489)
        self.assertEqual(meta.title, "Hades [Dash Only] by OckE")

    def test_it_says_it_was_seeded_so_a_rounded_duration_is_recognisable(self):
        video.seed("abc12345678", "t", 1489)
        self.assertTrue(self.entry("abc12345678")["seeded"])

    def test_a_real_probe_is_never_overwritten(self):
        path = Path(self.tmp.name) / "abc12345678.meta.json"
        path.write_text(json.dumps({"id": "abc12345678", "title": "probed",
                                    "duration": 1488, "channel": "ESA Speedrunning"}))
        self.assertFalse(video.seed("abc12345678", "searched", 1489))
        self.assertEqual(self.entry("abc12345678")["duration"], 1488)

    def test_a_row_with_no_duration_is_not_cached(self):
        # A zero-duration entry would make probe() raise on every later read,
        # which is worse than the request it saves.
        self.assertFalse(video.seed("abc12345678", "t", 0))
        self.assertFalse((Path(self.tmp.name) / "abc12345678.meta.json").exists())

    def test_a_row_with_no_video_id_is_not_cached(self):
        self.assertFalse(video.seed("", "t", 1489))


if __name__ == "__main__":
    unittest.main()
