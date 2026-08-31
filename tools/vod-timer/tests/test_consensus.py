"""Consensus tests, built from the shapes real ESA VODs actually produced.

Every series here is a run whose timer started `OFFSET` seconds before the
sampled window, so an honest frame at position p reads OFFSET + p until the
finish and holds its final value afterwards. The misreads are the ones the tool
really made - a `3` read as a `5`, in the digit position the source event had it.

Run with:  python -m unittest discover -s tools/vod-timer/tests
"""
import unittest

from vodtimer.consensus import Reading, resolve

STEP = 12.0
OFFSET = 1792.0          # 0:29:52 elapsed when the sampled window opens
FINISH_AT = 100.0        # so the true final time is 0:31:32
TRUTH = OFFSET + FINISH_AT


def series(plateau_values, ramp_frames=6, first_plateau_pos=106.0):
    """Ramp of honest frames, then the given tail one frame apart."""
    readings, i = [], 0
    start = first_plateau_pos - ramp_frames * STEP
    for n in range(ramp_frames):
        p = start + n * STEP
        readings.append(Reading(index=i, position=p, value=OFFSET + p))
        i += 1
    for n, v in enumerate(plateau_values):
        readings.append(Reading(index=i, position=first_plateau_pos + n * STEP,
                                value=v))
        i += 1
    return readings


class RampArbitratesThePlateau(unittest.TestCase):

    def test_clean_run_is_unchanged_and_high(self):
        r = resolve(series([TRUTH] * 7), duration=2000)
        self.assertEqual(r.final_seconds, TRUTH)
        self.assertEqual(r.confidence, "high")

    def test_inflated_plateau_loses_to_the_correct_one(self):
        """Both hold >= min_plateau frames; only one is on the ramp's line."""
        inflated = TRUTH + 1200            # a tens-of-minutes 3 read as a 5
        tail = [inflated, TRUTH, TRUTH, inflated, TRUTH, inflated, TRUTH]
        r = resolve(series(tail), duration=2000)
        self.assertEqual(r.final_seconds, TRUTH)
        self.assertEqual(r.confidence, "high")
        self.assertTrue(any("ramp agrees with" in x for x in r.reasons))

    def test_castlevania_true_value_read_fewer_times_than_the_misread(self):
        """0:51:32 five times against 0:31:32 twice; the ramp says 0:31:32.

        The truth is below min_plateau here, so it is never a plateau candidate.
        Only refusing the misread and falling back can reach it.
        """
        inflated = TRUTH + 1200
        tail = [inflated, TRUTH, inflated, inflated, TRUTH, inflated, inflated]
        r = resolve(series(tail), duration=2000)
        self.assertEqual(r.final_seconds, TRUTH)
        self.assertNotEqual(r.confidence, "high")   # honest: only two frames held

    def test_small_column_misread_is_caught_too(self):
        """Winter 2021's commonest shape: +2s, a units-of-seconds 3 read as 5."""
        inflated = TRUTH + 2
        tail = [inflated, TRUTH, TRUTH, inflated, TRUTH, TRUTH, TRUTH]
        r = resolve(series(tail), duration=2000)
        self.assertEqual(r.final_seconds, TRUTH)

    def test_fallback_ignores_a_reading_the_clock_could_not_have_reached(self):
        """No value repeats, so there is no plateau at all - only the fallback."""
        tail = [TRUTH + 1200, TRUTH + 1, TRUTH + 3, TRUTH + 5]
        r = resolve(series(tail), duration=2000, min_plateau=99)
        self.assertLess(r.final_seconds, TRUTH + 1200)
        self.assertTrue(any("fell back" in x for x in r.reasons))


class WithoutARampNothingChanges(unittest.TestCase):

    def test_too_few_ramp_frames_leaves_the_old_behaviour(self):
        """Under three agreeing pre-finish frames there is no ramp to trust."""
        inflated = TRUTH + 1200
        r = resolve(series([inflated] * 5, ramp_frames=2), duration=4000)
        self.assertEqual(r.final_seconds, inflated)

    def test_all_frames_after_the_finish_still_resolve(self):
        """A run that ended before the window opened has no ramp by definition."""
        readings = [Reading(index=i, position=100.0 + i * STEP, value=TRUTH)
                    for i in range(8)]
        r = resolve(readings, duration=2000)
        self.assertEqual(r.final_seconds, TRUTH)


if __name__ == "__main__":
    unittest.main()
