@extends('layouts.app')

@section('title', (isset($title)) ? $title : '')
@section('description', (isset($description)) ? $description : '')

@section('content')
	<?php /* @var $event App\Genre */ ?>
    <section class="main">
        <div class="container">
            <div class="row">
                <div class="col-md-12">
                    <nav aria-label="breadcrumb">
                        <ol class="breadcrumb bg-secondary py-0 px-0">
                            <li class="breadcrumb-item"><a href="/">Home</a></li>
                            <li class="breadcrumb-item"><a href="{{ route('genres') }}">Genres</a></li>
                            <li class="breadcrumb-item active" aria-current="page">{{ $genre->name }}</li>
                        </ol>
                    </nav>
                </div>
            </div>
            <div class="row justify-content-center">
                <div class="col-md-12">
                    <div class="jumbotron bg-primary py-5 mb-3">
                        <h1>{{ $genre->name }}</h1>
                        <hr class="my-4">
                        <p class="lead"><?= $genre->description ?></p>
                    </div>
                </div>
            </div>
            <div class="row justify-content-center">
                <div class="col-md-12">
                    @if($runs)
                        <table class="esa-table" id="mainTable">
                            <thead>
                                <tr>
                                    <th>Game</th>
                                    <th>Platform</th>
                                    <th>Category</th>
                                    <th>Event</th>
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
                                        @if(isset($run->game) && isset($run->game->slug))
                                            <a href="{{ route('game.show', $run->game->slug) }}" title="View all {{ $run->game->name }} runs at ESA">{{ $run->game->name }}</a>
                                        @endif
                                    </td>
                                    <td>
                                        @if(isset($run->platform->name) && isset($run->platform->slug))
                                            <a href="{{ route('platform.show', $run->platform->slug) }}" title="View all {{ $run->platform->name }} runs at ESA">{{ $run->platform->name }}</a>
                                        @endif
                                    </td>
                                    <td>{{ $run->category }}</td>
                                    <td>
                                        @if(isset($run->event->name) && isset($run->event->slug))
                                            <a href="{{ route('event.show', $run->event->slug) }}" title="View all {{ $run->event->name }} runs">{{ $run->event->name }}</a>
                                        @endif
                                    </td>
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
