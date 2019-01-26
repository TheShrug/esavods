@extends('layouts.app')

@section('title', (isset($title)) ? $title : '')
@section('description', (isset($description)) ? $description : '')

@section('content')
    <section class="main">
        <div class="container">
            <div class="row justify-content-center">
		        <?php /* @var $event App\Platform */ ?>
                <div class="col-md-12">
                    <div class="jumbotron bg-primary py-5">
                        <h2>About ESA VODs</h2>
                        <p>This site contains an archive of all known speedruns at the <a href="https://esamarathon.com/" target="_blank">European Speedrunner Assembly</a> Marathon. All credit belongs to ESA and the speedrunners involved. </p>
                        <p>Thank you to the creator of <a href="http://gdqvods.com/">gdqvods.com</a> for the inspiration to build this website. If you have any questions or concerns about the website, feel free to reach out and contact me.</p>
                        <hr class="my-4">
                        <div class="jumbo-links float-left">
                            <h5>ESA</h5>
                            <ul>
                                <li><a title="ESA on Twitter" target="_blank" href="https://www.twitter.com/esamarathon"><i class="fab fa-twitter"></i></a></li>
                                <li><a title="Join ESA's Discord server" target="_blank" href="https://www.discord.gg/0TZ2NlveujtasAqb"><i class="fab fa-discord"></i></a></li>
                                <li><a title="ESA on Youtube" target="_blank" href="https://www.youtube.com/user/EuroSpeedAssembly"><i class="fab fa-youtube"></i></a></li>
                                <li><a title="Check out the ESA channel on Twitch" target="_blank" href="https://www.twitch.tv/esamarathon"><i class="fab fa-twitch"></i></a></li>
                                <li><a title="ESA's forum on speedrun.com" target="_blank" href="https://www.speedrun.com/esa2018/forum"><i class="fas fa-comments"></i></a></li>
                                <li><a title="ESA on Facebook" target="_blank" href="https://www.facebook.com/europeanspeedrunnerassembly"><i class="fab fa-facebook"></i></a></li>
                            </ul>
                        </div>
                        <div class="jumbo-links float-right">
                            <h5>Contact</h5>
                            <ul>
                                <li><a href="mailto:esavods@gmail.com"><i class="fas fa-envelope"></i></a> <a href="mailto:esavods@gmail.com">esavods@gmail.com</a></li>
                                <li><i class="fab fa-discord"></i> Shrug#6348</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
@endsection
