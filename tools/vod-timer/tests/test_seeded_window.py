"""Recovering from a seeded duration that over-reported (#63).

`seed` writes a duration taken from a search result: rounded up by a second
across eight measured ESA uploads, and over-reported by 58 for one
third-party re-upload. The tail window's end *is* that duration, so an
over-estimate asks for footage past the end of the file, and the clip comes
back short of the window that was requested - indistinguishable, from the
clip alone, from the truncated download #63 refuses.

Nothing in the loop revisits a duration, so left alone that is a permanent
refusal: --resume re-reads the run and it fails identically, forever, with no
path back to a time that does not involve a person passing --tail or deleting
a cache entry by hand. `pipeline.fetch_window` spends the one request seeding
saved and asks for the true duration instead.

No event .conf sets a tail, so every backfill runs the default 780s and the
slack is 39s - these numbers are that default throughout.

Run with:  python -m unittest discover -s tools/vod-timer/tests
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from vodtimer import pipeline, video

TAIL = 780
TRUE_DURATION = 5000
SEEDED_DURATION = TRUE_DURATION + 58        # the re-upload's over-report


class KnowingWhereADurationCameFrom(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        patcher = mock.patch.dict("os.environ", {"VODTIMER_CACHE": self.tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_a_seeded_entry_says_so(self):
        video.seed("aaaaaaaaaaa", "Hades", SEEDED_DURATION)
        self.assertTrue(video.is_seeded("aaaaaaaaaaa"))

    def test_a_probed_entry_does_not(self):
        (Path(self.tmp.name) / "aaaaaaaaaaa.meta.json").write_text(json.dumps(
            {"id": "aaaaaaaaaaa", "title": "Hades", "duration": TRUE_DURATION,
             "channel": "ESA Speedrunning"}))
        self.assertFalse(video.is_seeded("aaaaaaaaaaa"))

    def test_an_unknown_video_does_not(self):
        self.assertFalse(video.is_seeded("aaaaaaaaaaa"))

    def test_refresh_replaces_a_seeded_entry_with_a_probed_one(self):
        video.seed("aaaaaaaaaaa", "Hades", SEEDED_DURATION)
        raw = json.dumps({"id": "aaaaaaaaaaa", "title": "Hades",
                          "duration": TRUE_DURATION, "channel": "ESA Speedrunning"})
        with mock.patch.object(video, "_run", return_value=raw) as run:
            meta = video.probe("aaaaaaaaaaa", refresh=True)
        self.assertEqual(run.call_count, 1)
        self.assertEqual(meta.duration, TRUE_DURATION)
        # And the recovery cannot recurse, because what it left behind is not
        # a seeded entry any more.
        self.assertFalse(video.is_seeded("aaaaaaaaaaa"))
        self.assertEqual(video.probe("aaaaaaaaaaa").duration, TRUE_DURATION)

    def test_without_refresh_the_cache_still_answers(self):
        video.seed("aaaaaaaaaaa", "Hades", SEEDED_DURATION)
        with mock.patch.object(video, "_run", side_effect=AssertionError("asked YouTube")):
            self.assertEqual(video.probe("aaaaaaaaaaa").duration, SEEDED_DURATION)


class AShortWindowFromASeededDuration(unittest.TestCase):
    """fetch_window with the two YouTube-facing calls stubbed: no requests are
    spent proving this, which is the whole point of counting them."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        patcher = mock.patch.dict("os.environ", {"VODTIMER_CACHE": self.tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.clip = Path(self.tmp.name) / "clip.mp4"
        self.clip.write_bytes(b"\0")
        self.windows: list[tuple[int, int]] = []

    def seeded_meta(self) -> video.Meta:
        video.seed("aaaaaaaaaaa", "Hades", SEEDED_DURATION)
        return video.probe("aaaaaaaaaaa")

    def probed_meta(self) -> video.Meta:
        (Path(self.tmp.name) / "aaaaaaaaaaa.meta.json").write_text(json.dumps(
            {"id": "aaaaaaaaaaa", "title": "Hades", "duration": SEEDED_DURATION,
             "channel": "ESA Speedrunning"}))
        return video.probe("aaaaaaaaaaa")

    def downloader(self, *lengths: float):
        """Each call returns a clip of the next length, or raises if it is
        materially shorter than the window that was asked for - which is what
        download_window itself does, with the real subprocesses removed."""
        lengths = list(lengths)

        def download(video_id, start, end, height, ytdlp_args=None):
            self.windows.append((start, end))
            got = lengths.pop(0)
            if not video.clip_is_complete(got, end - start):
                raise video.ShortClipError(f"{video_id}: only {got}s", got, end - start)
            return self.clip
        return mock.Mock(side_effect=download)

    def prober(self, duration=TRUE_DURATION):
        return mock.Mock(return_value=video.Meta(
            video_id="aaaaaaaaaaa", title="Hades", duration=duration))

    def fetch(self, meta, download, probe):
        with mock.patch.object(video, "download_window", download), \
             mock.patch.object(video, "probe", probe):
            return pipeline.fetch_window("aaaaaaaaaaa", meta, TAIL, 480)

    def test_the_58s_over_report_reads_instead_of_failing_forever(self):
        # The seeded window is 4278-5058; only 722s of it exists. The true
        # duration explains that, so the corrected window is read.
        meta, start, clip = self.fetch(
            self.seeded_meta(), self.downloader(722.0, 780.0), self.prober())
        self.assertEqual(clip, self.clip)
        self.assertEqual(meta.duration, TRUE_DURATION)
        self.assertEqual(start, TRUE_DURATION - TAIL)
        self.assertEqual(self.windows, [(SEEDED_DURATION - TAIL, SEEDED_DURATION),
                                        (TRUE_DURATION - TAIL, TRUE_DURATION)])

    def test_the_corrected_window_is_a_whole_tail_not_the_722s_that_survived(self):
        _, start, _ = self.fetch(
            self.seeded_meta(), self.downloader(722.0, 780.0), self.prober())
        second_start, second_end = self.windows[-1]
        self.assertEqual(second_end - second_start, TAIL)
        self.assertEqual(start, second_start)

    def test_it_costs_exactly_one_probe(self):
        probe = self.prober()
        self.fetch(self.seeded_meta(), self.downloader(722.0, 780.0), probe)
        self.assertEqual(probe.call_count, 1)
        self.assertEqual(probe.call_args.kwargs.get("refresh"), True)

    def test_a_genuine_truncation_still_fails_and_buys_no_second_download(self):
        # Same seeded entry, but the clip is the Summer 2022 shape: 110s of
        # 780. The true duration does not account for that, so the read is
        # refused - and the download is not repeated on the way out.
        download = self.downloader(110.0, 780.0)
        with self.assertRaises(video.ShortClipError):
            self.fetch(self.seeded_meta(), download, self.prober())
        self.assertEqual(download.call_count, 1)

    def test_a_probed_duration_is_never_re_probed(self):
        # Nothing to correct: an exact duration means a short clip is a short
        # download, and spending a request to be told so is a request wasted
        # against the wall.
        probe = self.prober()
        with self.assertRaises(video.ShortClipError):
            self.fetch(self.probed_meta(), self.downloader(110.0), probe)
        self.assertEqual(probe.call_count, 0)

    def test_a_clip_that_will_not_open_is_not_a_metadata_problem(self):
        # VideoError rather than ShortClipError, so the recovery must not fire.
        probe = self.prober()
        download = mock.Mock(side_effect=video.VideoError("moov atom not found"))
        with self.assertRaises(video.VideoError):
            self.fetch(self.seeded_meta(), download, probe)
        self.assertEqual(probe.call_count, 0)
        self.assertEqual(download.call_count, 1)

    def test_a_complete_window_asks_nothing_of_anyone(self):
        probe = self.prober()
        meta, start, _ = self.fetch(self.seeded_meta(), self.downloader(780.0), probe)
        self.assertEqual(probe.call_count, 0)
        self.assertEqual(meta.duration, SEEDED_DURATION)
        self.assertEqual(start, SEEDED_DURATION - TAIL)

    def test_the_one_second_rounding_never_reaches_the_recovery(self):
        # The ordinary case: seeded durations are a second long, and 1s is far
        # inside the slack, so this must not cost a probe at all.
        video.seed("aaaaaaaaaaa", "Hades", TRUE_DURATION + 1)
        probe = self.prober()
        self.fetch(video.probe("aaaaaaaaaaa"), self.downloader(779.0), probe)
        self.assertEqual(probe.call_count, 0)

    def test_a_video_shorter_than_the_tail_survives_the_recovery(self):
        # A seeded 120s VOD that is really 100s: the window is 0-120, only
        # 100s exists, and the corrected window is 0-100. Neither is a tail.
        video.seed("bbbbbbbbbbb", "Celeste", 120)
        seeded = video.probe("bbbbbbbbbbb")
        probe = mock.Mock(return_value=video.Meta(
            video_id="bbbbbbbbbbb", title="Celeste", duration=100))
        download = self.downloader(100.0, 100.0)
        with mock.patch.object(video, "download_window", download), \
             mock.patch.object(video, "probe", probe):
            meta, start, _ = pipeline.fetch_window("bbbbbbbbbbb", seeded, TAIL, 480)
        self.assertEqual((start, meta.duration), (0, 100))
        self.assertEqual(self.windows, [(0, 120), (0, 100)])


if __name__ == "__main__":
    unittest.main()
