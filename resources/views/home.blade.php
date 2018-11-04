@extends('layouts.app')

@section('title', (isset($title)) ? $title : '')
@section('description', (isset($description)) ? $description : '')

@section('content')
    <section class="main">
        <div class="container">
            <div class="row justify-content-center">
                <button class="testButton">button</button>
                <div class="col-md-12">
                    @if($runs)
                        <table class="table table-sm table-light mainDataTable">
                            <thead>
                            <tr>
                                <th></th>
                                <th>Game</th>
                                <th>Platform</th>
                                <th>Category</th>
                                <th>Event</th>
                                <th>Runners</th>
                                <th>Time</th>
                                <th>Play</th>
                            </tr>
                            </thead>
                            <tbody>
                                @foreach($runs as $run)
                                    <tr data-id="{{ $run->id }}">
                                        <td class="">
                                            <a href="#" class="btn btn-sm btn-primary expand-row-button"></a>
                                        </td>
                                        <td>
                                            @if(isset($run->game) && isset($run->game->slug))
                                                <a href="{{ route('game.show', $run->game->slug) }}" title="{{ $run->game->name }}">{{ $run->game->name }}</a>
                                            @endif
                                        </td>
                                        <td>
                                            @if(isset($run->platform->name) && isset($run->platform->slug))
                                                <a href="{{ route('platform.show', $run->platform->slug) }}" title="{{ $run->platform->name }}">{{ $run->platform->name }}</a>
                                            @endif
                                        </td>
                                        <td>{{ $run->category }}</td>
                                        <td>
                                            @if(isset($run->event->name) && isset($run->event->slug))
                                                <a href="{{ route('event.show', $run->event->slug) }}" title="{{ $run->event->name }}">{{ $run->event->name }}</a>
                                            @endif
                                        </td>
                                        <td>
                                            @foreach($run->runners as $key => $runner)
                                                @if(isset($runner->name) && isset($runner->slug))
                                                    <a href="{{ route('runner.show', $runner->slug) }}" title="{{ $runner->name }}">{{ $runner->name }}</a>
                                                @endif
                                            @endforeach
                                        </td>
                                        <td>{{ $run->time }}</td>
                                        <td><i class="fa fa-play"></i></td>
                                    </tr>

                                @endforeach
                            </tbody>
                        </table>
                    @endif;
                </div>
            </div>
        </div>
    </section>
@endsection
