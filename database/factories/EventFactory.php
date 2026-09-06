<?php

namespace Database\Factories;

use App\Event;
use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Str;

/**
 * @extends Factory<Event>
 */
class EventFactory extends Factory
{
    /**
     * The model this factory builds. This app keeps its models in App\, not
     * App\Models\, so the convention-based lookup does not find it.
     *
     * @var class-string<Event>
     */
    protected $model = Event::class;

    /**
     * Define the model's default state.
     *
     * Name and slug are derived from one unique token rather than faked
     * independently: every show route looks the row up BY SLUG, so two rows
     * that collide on slug make `firstOrFail()` return the wrong one and a
     * test fail somewhere unrelated to what it was checking.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        $name = 'ESA ' . fake()->unique()->words(2, true);

        return [
            'name' => Str::title($name),
            'slug' => Str::slug($name),
            'description' => fake()->sentence(),
            // No year or order: the menu's ordering comes from MIN(run_date)
            // over the event's runs (#98), so an event that needs a place in
            // that order needs runs with dates, not a column set here.
        ];
    }
}
