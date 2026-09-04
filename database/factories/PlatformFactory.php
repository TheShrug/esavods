<?php

namespace Database\Factories;

use App\Platform;
use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Str;

/**
 * @extends Factory<Platform>
 */
class PlatformFactory extends Factory
{
    /**
     * The model this factory builds. This app keeps its models in App\, not
     * App\Models\, so the convention-based lookup does not find it.
     *
     * @var class-string<Platform>
     */
    protected $model = Platform::class;

    /**
     * Define the model's default state.
     *
     * Name and slug come from one unique token: the show route looks the row
     * up by slug, so a collision silently returns the wrong platform.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        $name = fake()->unique()->words(3, true);

        return [
            'name' => Str::title($name),
            'slug' => Str::slug($name),
            'description' => fake()->sentence(),
        ];
    }
}
