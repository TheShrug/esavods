@extends('layouts.app')

@section('title', (isset($title)) ? $title : '')
@section('description', (isset($description)) ? $description : '')

@section('content')
	<?php /* @var $event App\Event */ ?>
    <section class="main">
        <div class="container">
            <div class="row">
                <div class="col-md-12">
                    <nav aria-label="breadcrumb">
                        <ol class="breadcrumb bg-secondary py-0 px-0">
                            <li class="breadcrumb-item"><a href="/">Home</a></li>
                            <li class="breadcrumb-item"><a href="{{ route('events') }}">Events</a></li>
                            <li class="breadcrumb-item active" aria-current="page">{{ $event->name }}</li>
                        </ol>
                    </nav>
                </div>
            </div>
            <div class="row justify-content-center">
                <div class="col-md-12">
                    <div class="jumbotron bg-primary py-5 mb-3">
                        <h1>{{ $event->name }}</h1>
                        <hr class="my-4">
                        <p class="lead"><?= $event->description ?></p>
                    </div>
                </div>
            </div>
            <div class="row justify-content-center">
                <div class="col-md-12">
                    @if($runs)
                        <table class="esa-table" id="mainTable" data-order="[[0,&quot;asc&quot;]]">
                            <thead>
                                <tr>
                                    <th>Schedule Time</th>
                                    <th>Game</th>
                                    <th>Category</th>
                                    <th>Platform</th>
                                    <th>Runners</th>
                                    <th>Time</th>
                                    <th data-sortable="false" data-priority="1">Play</th>
                                </tr>
                            </thead>
                            <tbody>
                            @foreach($runs as $run)
	                            <?php /* @var $run \App\Run */ ?>
                                <tr data-id="{{ $run->id }}">
                                    <td data-order="{{{ isset($run->run_date) ? $run->run_date : '' }}}">
                                        @if(isset($run->run_date))
                                            {{ Date('D M jS, h:ia', strtotime($run->run_date)) }}
                                        @endif
                                    </td>
                                    <td>
                                        @if(isset($run->game) && isset($run->game->slug))
                                            <a href="{{ route('game.show', $run->game->slug) }}" title="View all {{ $run->game->name }} runs at ESA">{{ $run->game->name }}</a>
                                        @endif
                                    </td>
                                    <td>{{ $run->category }}</td>
                                    <td>
                                        @if(isset($run->platform->name) && isset($run->platform->slug))
                                            <a href="{{ route('platform.show', $run->platform->slug) }}" title="View all {{ $run->platform->name }} runs at ESA">{{ $run->platform->name }}</a>
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
                                        <a href="#" class="close-vod"><i class="fas fa-times"></i></a>
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
