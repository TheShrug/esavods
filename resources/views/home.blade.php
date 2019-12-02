@extends('layouts.app')

@section('title', (isset($title)) ? $title : '')
@section('description', (isset($description)) ? $description : '')

@section('content')
    <section class="main">
        <div class="container">
            <div class="row justify-content-center">
		        <?php /* @var $event App\Platform */ ?>
                <div class="col-md-12">
                    <div class="jumbotron bg-primary py-5 mb-3">
                        <h1>Welcome to ESA VODs</h1>
                        <p>Navigate all speedrunning VODs of the <a href="https://esamarathon.com/" target="_blank">European Speedrunner Assembly</a> marathon online. This site contains an archive of all known speedruns at the European Speedrunner Assembly Marathon. All credit belongs to ESA and the speedrunners involved. The table below displays the top 100 most watched runs and resets at the conclusion of each marathon.</p>
                        <p class="lead">Thank you <a href="https://esamarathon.com/" target="_blank">ESA</a> & <a href="https://dreamhack.com/" target="_blank">Dreamhack</a> for this most recent event! The latest vods for ESA Dreamhack Winter 2019 can be found here:
                            <a href="https://esavods.com/event/esa-dreamhack-winter-2019" title="ESA Vods for Dreamhack 2019 Winter">Dreamhack 2019 Winter</a></p>
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
                            <h5 class="text-right">Contact</h5>
                            <ul>
                                <li><a href="mailto:esavods@gmail.com"><a href="mailto:esavods@gmail.com">esavods@gmail.com</a></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row justify-content-center">
                <div class="col-md-12">
                    @if($runs)
                        <table class="esa-table" id="mainTable" data-order="[]">
                            <thead>
                            <tr>
                                <th>Game</th>
                                <th>Event</th>
                                <th>Platform</th>
                                <th>Category</th>
                                <th>Runners</th>
                                <th>Time</th>
                                {{--<th>Genres</th>--}}
                                <th data-sortable="false" data-priority="1">Play</th>
                            </tr>
                            </thead>
                            <tbody>
                                @foreach($runs as $run)
                                    <?php /* @var $run \App\Run */ ?>
                                    <tr data-id="{{ $run->id }}">
                                        <td>
                                            @if(isset($run->game) && isset($run->game->slug))
                                                <a href="{{ route('game.show', $run->game->slug) }}" title="View all {{ $run->game->name }} runs at ESA">{{ $run->game->name }}</a>
                                            @endif
                                        </td>
                                        <td>
                                            @if(isset($run->event->name) && isset($run->event->slug))
                                                <a href="{{ route('event.show', $run->event->slug) }}" title="View all {{ $run->event->name }} runs">{{ $run->event->name }}</a>
                                            @endif
                                        </td>
                                        <td>
                                            @if(isset($run->platform->name) && isset($run->platform->slug))
                                                <a href="{{ route('platform.show', $run->platform->slug) }}" title="View all {{ $run->platform->name }} runs at ESA">{{ $run->platform->name }}</a>
                                            @endif
                                        </td>
                                        <td>{{ $run->category }}</td>
                                        <td>
                                            @foreach($run->runners as $key => $runner)
                                                @if(isset($runner->name) && isset($runner->slug))
                                                    <a href="{{ route('runner.show', $runner->slug) }}" title="View runs by {{ $runner->name }}">{{ $runner->name }}</a>
                                                @endif
                                            @endforeach
                                        </td>
                                        <td>{{ gmdate('H:i:s', $run->time) }}</td>
                                        {{--<td>--}}
                                            {{--@foreach($run->genres as $key => $genre)--}}
                                                {{--@if(isset($genre->name) && isset($genre->slug))--}}
                                                    {{--<a href="{{ route('genre.show', $genre->slug) }}" title="View more games in the {{ $genre->name }} genre">{{ $genre->name }}</a>--}}
                                                {{--@endif--}}
                                            {{--@endforeach--}}
                                        {{--</td>--}}
                                        <td class="video-links" nowrap>
                                            @if(isset($run->youtube_vod_id))
                                                <a class="youtube" href="https://youtube.com/watch?v={{ $run->youtube_vod_id }}" title="Youtube Link" data-vod-site="youtube" data-vod="{{ $run->youtube_vod_id }}"><i class="fab fa-youtube"></i></a>
                                            @endif
                                            @if(isset($run->twitch_vod_id))
                                                <a class="twitch" href="https://www.twitch.tv/videos/{{ $run->twitch_vod_id }}" title="Twitch Link" data-vod-site="twitch" data-vod="{{ $run->twitch_vod_id }}"><i class="fab fa-twitch"></i></a>
                                            @endif
                                                <a href="#" class="close-vod"><i class="fas fa-times"></i></a>
                                        </td>
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    @endif
                </div>
                <div class="col-md-6"></div>
            </div>
        </div>
    </section>
@endsection
