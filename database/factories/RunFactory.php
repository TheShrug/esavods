<?php

namespace Database\Factories;

use App\Event;
use App\Game;
use App\Platform;
use App\Run;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<Run>
 */
class RunFactory extends Factory
{
    /**
     * The model this factory builds. This app keeps its models in App\, not
     * App\Models\, so the convention-based lookup does not find it.
     *
     * @var class-string<Run>
     */
    protected $model = Run::class;

    /**
     * Define the model's default state.
     *
     * `category` is a plain string column on runs and is NOT the App\Category
     * relationship - the two are unrelated, and every run table renders the
     * string while /category/{slug} filters on the relationship. A run that
     * needs both wants create(['category' => $category->name]) AND
     * $category->runs()->attach($run) - setting one does not set the other.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        return [
            // Seconds. Deliberately under an hour by default so the padded
            // "00:MM:SS" shape is the common case; overTwentyFourHours()
            // covers the wrap that broke gmdate().
            'time' => fake()->numberBetween(600, 3599),
            'category' => 'Any%',
            'twitch_vod_id' => (string) fake()->numberBetween(100000000, 999999999),
            'youtube_vod_id' => fake()->regexify('[A-Za-z0-9_-]{11}'),
            'event_id' => Event::factory(),
            'platform_id' => Platform::factory(),
            'game_id' => Game::factory(),
            // A string, not a DateTime: run_date has no cast, so Eloquent hands
            // back whatever was set. The event page calls strtotime() on it,
            // which TypeErrors on an object - a fresh read from the database
            // would be a string, so a DateTime here only fails in tests.
            'run_date' => fake()->dateTimeBetween('-6 years', 'now')->format('Y-m-d H:i:s'),
        ];
    }

    /**
     * A run longer than a day. ESA Summer 2025's Final Fantasy IX Vivi% ran
     * 24:05:51 and the old gmdate('H:i:s') formatting displayed it as
     * 00:05:51 - see Run::getFormattedTimeAttribute().
     */
    public function overTwentyFourHours(): static
    {
        return $this->state(fn (array $attributes) => [
            'time' => 86751, // 24:05:51
        ]);
    }

    /**
     * A run with neither VOD id, so the play column's two @if branches are
     * coverable both ways.
     */
    public function withoutVods(): static
    {
        return $this->state(fn (array $attributes) => [
            'twitch_vod_id' => null,
            'youtube_vod_id' => null,
        ]);
    }
}
