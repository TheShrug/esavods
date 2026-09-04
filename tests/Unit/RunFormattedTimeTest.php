<?php

namespace Tests\Unit;

use App\Run;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;

/**
 * Run::getFormattedTimeAttribute().
 *
 * Every run table on the site prints this and nothing else, so it is the one
 * piece of formatting worth a unit test. The views used to call
 * gmdate('H:i:s', $time), which formats an INSTANT rather than a duration - its
 * H is an hour-of-day and wraps at 24. ESA Summer 2025's Final Fantasy IX Vivi%
 * ran 24:05:51 and displayed as 00:05:51, a five-minute run on a page whose
 * whole purpose is run times. The 24-hour case below is that bug.
 *
 * No database and no application: the accessor reads one attribute.
 */
class RunFormattedTimeTest extends TestCase
{
    /**
     * @return array<string, array{int|float, string}>
     */
    public static function times(): array
    {
        return [
            'zero' => [0, '00:00:00'],
            'seconds only' => [7, '00:00:07'],
            'minutes' => [4530, '01:15:30'],
            'fractional seconds truncate' => [4530.998, '01:15:30'],
            'just under a day' => [86399, '23:59:59'],
            'exactly a day' => [86400, '24:00:00'],
            'the Vivi% run' => [86751, '24:05:51'],
            'past 99 hours, unpadded rather than truncated' => [360000, '100:00:00'],
        ];
    }

    #[DataProvider('times')]
    public function test_it_formats_a_duration(int|float $seconds, string $expected): void
    {
        $run = new Run(['time' => $seconds]);

        $this->assertSame($expected, $run->formatted_time);
    }
}
