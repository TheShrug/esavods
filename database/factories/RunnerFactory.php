<?php

namespace Database\Factories;

use App\Runner;
use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Str;

/**
 * @extends Factory<Runner>
 */
class RunnerFactory extends Factory
{
    /**
     * The model this factory builds. This app keeps its models in App\, not
     * App\Models\, so the convention-based lookup does not find it.
     *
     * @var class-string<Runner>
     */
    protected $model = Runner::class;

    /**
     * Define the model's default state.
     *
     * Name and slug come from one unique token: /runner/{slug} looks the row
     * up by slug, so a collision silently returns the wrong runner.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        $name = fake()->unique()->userName();

        return [
            'name' => $name,
            'slug' => Str::slug($name),
            'twitch' => fake()->userName(),
            'twitter' => fake()->userName(),
            'youtube' => fake()->userName(),
        ];
    }

    /**
     * A runner with no social links, so the runner page's
     * `@if(!empty($runner->twitch) || ...)` block is coverable both ways.
     */
    public function withoutSocials(): static
    {
        return $this->state(fn (array $attributes) => [
            'twitch' => null,
            'twitter' => null,
            'youtube' => null,
        ]);
    }
}
