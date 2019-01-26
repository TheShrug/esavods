<?php

namespace App\Console\Commands;

use App\User;
use Illuminate\Console\Command;
use Hash;

class CreateUser extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'user:create';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Create a user that can access the dashboard';

    /**
     * Create a new command instance.
     *
     * @return void
     */
    public function __construct()
    {
        parent::__construct();
    }

    /**
     * Execute the console command.
     *
     * @return mixed
     */
    public function handle()
    {
	    $name = $this->ask('Name?');
        $email = $this->ask('Email Address?');
        $password = $this->ask('Password?');

        $user = new User();
        $user->password = Hash::make($password);
        $user->name = $name;
        $user->email = $email;
        $user->save();
    }
}
