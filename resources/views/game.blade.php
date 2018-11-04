@extends('layouts.app')

@section('title', 'Title')
@section('description', 'Description')

@section('content')
    <section class="main">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-12">
                    @if($runs)
                        <table class="table table-sm table-striped table-hover table-light">
                            <thead>
                            <tr>
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
                                <tr>
                                    <td><a href="{{ route('game.show', $run->game->slug) }}" title="{{ $run->game->name }}">{{ $run->game->name }}</a></td>
                                    <td>{{ $run->platform->name }}</td>
                                    <td>{{ $run->category }}</td>
                                    <td>{{ $run->event->name }}</td>
                                    <td>
										<?php $runners =  ''; ?>

                                        {{ $run->runners[0]->name }}

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
