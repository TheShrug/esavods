@extends('layouts.app')

@section('title', (isset($title)) ? $title : '')
@section('description', (isset($description)) ? $description : '')

@section('content')
    <section class="main">
        <div class="container">
            <div class="row">
                <div class="col-md-12">
                    <nav aria-label="breadcrumb">
                        <ol class="breadcrumb bg-secondary py-0 px-0">
                            <li class="breadcrumb-item"><a href="/">Home</a></li>
                            <li class="breadcrumb-item active" aria-current="page">Games</li>
                        </ol>
                    </nav>
                </div>
            </div>
            <div class="row justify-content-center">
                <div class="col-md-12">
                    @if($games)
                        <table class="esa-table" id="mainTable" data-order="[[0,&quot;asc&quot;]]">
                            <thead>
                                <tr>
                                    <th>Game</th>
                                    <th>Number of Runs</th>
                                </tr>
                            </thead>
                            <tbody>
                            @foreach($games as $game)
	                            <?php /* @var $event \App\Event */ ?>
                                <tr data-id="{{ $game->id }}">
                                    <td nowrap>
                                        @if(isset($game->name) && isset($game->slug))
                                            <a href="{{ route('game.show', $game->slug) }}">{{ $game->name }}</a>
                                        @endif
                                    </td>
                                    <td>
                                       @if(isset($game->runs_count))
                                           {{ $game->runs_count }}
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
