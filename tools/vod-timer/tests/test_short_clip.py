"""A truncated download must not pass for a complete one (#63).

When a range request is throttled or refused partway, yt-dlp exits 0 having
written a valid, playable, *short* clip. Two ESA Summer 2022 re-reads came
back with 11 and 14 frames where 50 were expected, and both produced
confident-looking times from a window that never contained the finish -
Shadow Warrior 3 read 0:44:56 against a published 0:50:55 it had previously
read exactly.

A byte count cannot tell those apart from a real clip: 50 seconds of 480p
clears MIN_CLIP_BYTES comfortably. The clip's measured duration can, so these
tests are about that measurement, the slack it allows, and what
`download_window` does with the answer - including the cached copy, which the
old code kept and reused on every later run.

Run with:  python -m unittest discover -s tools/vod-timer/tests
"""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from vodtimer import video

HAS_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
NEEDS_FFMPEG = "needs ffmpeg/ffprobe - both are in the vod-timer image"


def fault(seconds: float, start: int, end: int) -> str | None:
    """`_clip_fault` for a clip that measures `seconds`, without an ffprobe."""
    with mock.patch.object(video, "clip_duration", return_value=seconds):
        return video._clip_fault(Path("clip.mp4"), start, end)


class MeasuringAClip(unittest.TestCase):
    """clip_duration against real files, so the ffprobe wiring is proven."""

    @unittest.skipUnless(HAS_FFMPEG, NEEDS_FFMPEG)
    def test_it_reads_the_length_of_a_real_clip(self):
        with tempfile.TemporaryDirectory() as tmp:
            clip = Path(tmp) / "clip.mp4"
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
                 "-i", "testsrc=size=320x240:rate=10:duration=8", str(clip)],
                check=True,
            )
            self.assertAlmostEqual(video.clip_duration(clip), 8.0, delta=0.5)

    @unittest.skipUnless(HAS_FFMPEG, NEEDS_FFMPEG)
    def test_a_file_ffmpeg_cannot_open_raises_rather_than_reading_as_zero(self):
        # The #67 shape: a file large enough to pass the size check with no
        # moov atom in it. It must be an outright fault, not a zero-length clip.
        with tempfile.TemporaryDirectory() as tmp:
            junk = Path(tmp) / "clip.mp4"
            junk.write_bytes(b"\0" * (video.MIN_CLIP_BYTES + 1))
            with self.assertRaises(video.VideoError):
                video.clip_duration(junk)


class DecidingWhetherAClipIsShort(unittest.TestCase):
    def test_the_summer_2022_truncation_is_caught(self):
        # 11 frames at 10s spacing is ~110s of the 780s tail that was asked for.
        self.assertIsNotNone(fault(110.0, 4000, 4780))

    def test_a_complete_clip_passes(self):
        self.assertIsNone(fault(780.0, 4000, 4780))

    def test_a_keyframe_second_or_two_is_not_a_truncation(self):
        self.assertIsNone(fault(778.4, 4000, 4780))

    def test_a_video_shorter_than_the_tail_is_judged_by_its_own_window(self):
        # pipeline.py computes start = max(0, duration - tail), so a two-minute
        # VOD legitimately asks for 0-120 and is complete at 120s. Compared
        # against --tail instead, every short VOD in the event would fail.
        self.assertIsNone(fault(120.0, 0, 120))

    def test_a_short_window_still_gets_the_floor_of_slack(self):
        # 5% of 120s is under the floor; the keyframe cut does not care how
        # short the window was.
        self.assertIsNone(fault(116.0, 0, 120))

    def test_but_a_short_window_that_arrived_truncated_is_still_caught(self):
        self.assertIsNotNone(fault(20.0, 0, 120))

    def test_a_clip_that_will_not_open_is_a_fault_too(self):
        with mock.patch.object(video, "clip_duration",
                               side_effect=video.VideoError("moov atom not found")):
            self.assertIsNotNone(video._clip_fault(Path("clip.mp4"), 4000, 4780))

    def test_the_message_says_what_came_back_and_what_was_asked_for(self):
        # This string is what cmd_batch puts in the results CSV's `notes`, so
        # it is the whole of what a person sees when a read is refused.
        msg = fault(110.0, 4000, 4780)
        self.assertIn("110s", msg)
        self.assertIn("780s", msg)
        self.assertIn("4000-4780s", msg)


class DownloadWindowRefusesAShortClip(unittest.TestCase):
    """The download path end to end with both subprocesses stubbed out: no
    network and no ffmpeg, which is the point - proving this with a live
    download would spend requests against YouTube's wall."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        patcher = mock.patch.dict("os.environ", {"VODTIMER_CACHE": self.tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.cache = Path(self.tmp.name)
        self.downloads = 0

    def stub(self, seconds: float, size: int = video.MIN_CLIP_BYTES + 1):
        """yt-dlp writes a big enough file; ffprobe says it is `seconds` long."""
        def run(cmd, timeout=900):
            if cmd[0] == "yt-dlp":
                self.downloads += 1
                out = Path(cmd[cmd.index("-o") + 1].replace("%(ext)s", "mp4"))
                out.write_bytes(b"\0" * size)
                return ""
            if cmd[0] == "ffprobe":
                return str(seconds) + "\n"
            raise AssertionError("unexpected command " + cmd[0])
        return mock.patch.object(video, "_run", side_effect=run)

    def clips(self) -> list[Path]:
        return [p for p in self.cache.iterdir()
                if p.is_file() and p.suffix != ".json"]

    def test_a_complete_download_is_returned_and_cached(self):
        with self.stub(780.0):
            clip = video.download_window("aaaaaaaaaaa", 4000, 4780, 480)
        self.assertTrue(clip.exists())
        self.assertEqual(self.clips(), [clip])

    def test_a_short_download_raises_instead_of_being_read(self):
        with self.stub(110.0):
            with self.assertRaises(video.VideoError) as caught:
                video.download_window("aaaaaaaaaaa", 4000, 4780, 480)
        self.assertIn("110s", str(caught.exception))
        self.assertIn("aaaaaaaaaaa", str(caught.exception))

    def test_a_short_download_leaves_nothing_in_the_cache(self):
        # Otherwise the next run - --resume included, which is the run meant to
        # fix it - reads the same truncated window straight back out.
        with self.stub(110.0):
            with self.assertRaises(video.VideoError):
                video.download_window("aaaaaaaaaaa", 4000, 4780, 480)
        self.assertEqual(self.clips(), [])

    def test_a_good_clip_in_the_cache_costs_no_download(self):
        with self.stub(780.0):
            first = video.download_window("aaaaaaaaaaa", 4000, 4780, 480)
            second = video.download_window("aaaaaaaaaaa", 4000, 4780, 480)
        self.assertEqual(first, second)
        self.assertEqual(self.downloads, 1)

    def test_a_short_clip_already_in_the_cache_is_dropped_not_reused(self):
        # The Summer 2022 state: a truncated clip that passed the size check,
        # left in the cache by an earlier run.
        with self.stub(780.0):
            video.download_window("aaaaaaaaaaa", 4000, 4780, 480)
        self.downloads = 0
        with self.stub(110.0):                    # it was short all along
            with self.assertRaises(video.VideoError):
                video.download_window("aaaaaaaaaaa", 4000, 4780, 480)
        self.assertEqual(self.downloads, 1, "the cached clip was reused")
        self.assertEqual(self.clips(), [])

    def test_a_cached_clip_ffmpeg_cannot_open_is_dropped_too(self):
        # #67's second half: those files were large enough to pass the size
        # check, so every retry reused the corrupt clip and reproduced the same
        # `moov atom not found`, and the cache entry had to be deleted by hand.
        with self.stub(780.0):
            video.download_window("aaaaaaaaaaa", 4000, 4780, 480)
        self.downloads = 0

        def broken(cmd, timeout=900):
            if cmd[0] == "ffprobe":
                raise video.VideoError("ffprobe failed (183): moov atom not found")
            self.downloads += 1
            out = Path(cmd[cmd.index("-o") + 1].replace("%(ext)s", "mp4"))
            out.write_bytes(b"\0" * (video.MIN_CLIP_BYTES + 1))
            return ""

        with mock.patch.object(video, "_run", side_effect=broken):
            with self.assertRaises(video.VideoError):
                video.download_window("aaaaaaaaaaa", 4000, 4780, 480)
        self.assertEqual(self.downloads, 1, "the unopenable clip was reused")
        self.assertEqual(self.clips(), [])

    def test_a_stub_below_the_size_check_is_still_refused(self):
        with self.stub(780.0, size=1024):
            with self.assertRaises(video.VideoError):
                video.download_window("aaaaaaaaaaa", 4000, 4780, 480)
        self.assertEqual(self.clips(), [])


if __name__ == "__main__":
    unittest.main()
