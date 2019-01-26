@extends('layouts.app')

@section('title', 'Title')
@section('description', 'Description')

@section('content')
<section class="main">
    <div class="container">
        <div class="row justify-content-center">
		    <?php /* @var $event App\Game */ ?>
            <div class="col-md-12">
                <div class="jumbotron bg-primary py-5">
                    <h1>{{ $game->name }}</h1>
                    <hr class="my-4">
                    <p class="lead"><?= $game->description ?></p>
                </div>
            </div>
        </div>
        <div class="row justify-content-center">
            <div class="col-md-12">
                @if($runs)
                    <table class="esa-table" id="mainTable">
                        <thead>
                        <tr>
                            <th>Event</th>
                            <th>Category</th>
                            <th>Runners</th>
                            <th>Time</th>
                            <th data-sortable="false" data-priority="1">Play</th>
                        </tr>
                        </thead>
                        <tbody>
                        @foreach($runs as $run)
                            <?php /* @var $run \App\Run */ ?>
                            <tr data-id="{{ $run->id }}">
                                <td>
                                    @if(isset($run->event->name) && isset($run->event->slug))
                                        <a href="{{ route('event.show', $run->event->slug) }}" title="View all {{ $run->event->name }} runs">{{ $run->event->name }}</a>
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
                                <td class="video-links" nowrap>
                                    @if(isset($run->youtube_vod_id))
                                        <a class="youtube" href="https://youtube.com/watch?v={{ $run->youtube_vod_id }}" title="Youtube Link" data-vod-site="youtube" data-vod="{{ $run->youtube_vod_id }}"><i class="fab fa-youtube"></i></a>
                                    @endif
                                    @if(isset($run->twitch_vod_id))
                                        <a class="twitch" href="https://www.twitch.tv/videos/{{ $run->twitch_vod_id }}" title="Twitch Link" data-vod-site="twitch" data-vod="{{ $run->twitch_vod_id }}"><i class="fab fa-twitch"></i></a>
                                    @endif
                                </td>
                            </tr>
                        @endforeach
                        </tbody>
                    </table>
                @endif
            </div>
        </div>
    </div>
</section>
@endsection
