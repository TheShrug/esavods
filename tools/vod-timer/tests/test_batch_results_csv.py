"""What a batch writes down, and what --resume does with it afterwards (#63).

Two of the four things #63 asks for live here rather than in video.py:

  - `frames_read`/`frames_total` have to reach the results CSV. `_report`
    printed them all along, but the printout is a container log; the CSV is
    what a person reads afterwards, and the two truncated Summer 2022 rows
    carried a final_time, a confidence and notes that all looked ordinary.
  - a refused read has to be retried by --resume rather than standing as an
    answer, which works because "done" means "produced a time", not "has a
    row".

Run with:  python -m unittest discover -s tools/vod-timer/tests
"""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from vodtimer import cli, video


def read(video_id="aaaaaaaaaaa", **over) -> dict:
    """What `analyse` hands back for a clean read."""
    r = {
        "video_id": video_id, "title": "Hades [Dash Only] by OckE",
        "duration": 1489, "duration_hms": "0:24:49", "estimate": "",
        "crop": [810, 62, 190, 44], "calibration": {"agreed": 5, "sampled": 6},
        "window": [709, 1489], "step": 10.0,
        "final_seconds": 1481.0, "final_time": "0:24:41", "confidence": "high",
        "reasons": ["plateau of 9 frames"], "plateau_starts_at": 1380.0,
        "frames_read": 50, "frames_total": 50,
    }
    r.update(over)
    return r


TRUNCATED = video.VideoError(
    "aaaaaaaaaaa: clip is only 110s of the 780s window 709-1489s that was "
    "requested - the download stopped early, so the finish may never be on "
    "screen"
)


class BatchResults(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.out = self.dir / "results.csv"
        self.input = self.dir / "runs.csv"
        self.input.write_text("video_id,game,estimate\n"
                              "aaaaaaaaaaa,Hades,0:25:00\n", encoding="utf8")

    def batch(self, analyse, resume=False) -> mock.Mock:
        argv = ["batch", str(self.input), "--out", str(self.out)]
        if resume:
            argv.append("--resume")
        with mock.patch.object(cli, "analyse", analyse) as m:
            cli.main(argv)
        return m

    def rows(self) -> list[dict]:
        with open(self.out, encoding="utf8") as fh:
            return list(csv.DictReader(fh))

    def test_frames_read_and_total_reach_the_csv(self):
        self.batch(mock.Mock(side_effect=[read()]))
        row = self.rows()[0]
        self.assertEqual(row["frames_read"], "50")
        self.assertEqual(row["frames_total"], "50")

    def test_a_short_read_is_visible_in_the_csv_without_the_logs(self):
        # The Shadow Warrior 3 row, had the clip check not refused it first:
        # 11 frames of the 50 the window should have held.
        self.batch(mock.Mock(side_effect=[read(frames_read=11, frames_total=11)]))
        self.assertEqual(self.rows()[0]["frames_read"], "11")

    def test_a_refused_read_records_the_message_and_no_time(self):
        self.batch(mock.Mock(side_effect=TRUNCATED))
        row = self.rows()[0]
        self.assertEqual(row["final_time"], "")
        self.assertEqual(row["confidence"], "none")
        self.assertIn("110s of the 780s window", row["notes"])

    def test_resume_re_reads_a_refused_row(self):
        self.batch(mock.Mock(side_effect=TRUNCATED))
        again = self.batch(mock.Mock(side_effect=[read()]), resume=True)
        self.assertEqual(again.call_count, 1)
        rows = self.rows()
        self.assertEqual(len(rows), 1)               # not two rows for one video
        self.assertEqual(rows[0]["final_time"], "0:24:41")

    def test_resume_leaves_a_row_that_produced_a_time_alone(self):
        self.batch(mock.Mock(side_effect=[read()]))
        again = self.batch(mock.Mock(side_effect=[read()]), resume=True)
        self.assertEqual(again.call_count, 0)
        self.assertEqual(self.rows()[0]["frames_read"], "50")

    def test_resume_over_a_csv_written_before_these_columns_existed(self):
        # Results already on disk from an earlier version have no frames
        # columns. Their rows are copied forward, so they must not blow up the
        # writer or lose the time they carry.
        self.out.write_text(
            "video_id,game,actual,final_time,final_seconds,confidence,"
            "duration,estimate,check_at,crop,notes\n"
            "bbbbbbbbbbb,Celeste,,0:33:12,1992.0,high,2100,,1900,\"1,2,3,4\",\n",
            encoding="utf8")
        self.batch(mock.Mock(side_effect=[read()]), resume=True)
        rows = {r["video_id"]: r for r in self.rows()}
        self.assertEqual(rows["bbbbbbbbbbb"]["final_time"], "0:33:12")
        self.assertEqual(rows["bbbbbbbbbbb"]["frames_read"], "")
        self.assertEqual(rows["aaaaaaaaaaa"]["frames_read"], "50")


if __name__ == "__main__":
    unittest.main()
