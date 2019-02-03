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
                            <li class="breadcrumb-item active" aria-current="page">Events</li>
                        </ol>
                    </nav>
                </div>
            </div>
            <div class="row justify-content-center">
                <div class="col-md-12">
                    @if($events)
                        <table class="esa-table" id="mainTable" data-order="[[0,&quot;asc&quot;]]">
                            <thead>
                                <tr>
                                    <th>Event</th>
                                    <th data-orderable="false">Description</th>
                                    <th data-orderable="false">Number of Runs</th>
                                </tr>
                            </thead>
                            <tbody>
                            @foreach($events as $event)
	                            <?php /* @var $event \App\Event */ ?>
                                <tr data-id="{{ $event->id }}">
                                    <td nowrap>
                                        @if(isset($event->name) && isset($event->slug))
                                            <a href="{{ route('event.show', $event->slug) }}">{{ $event->name }}</a>
                                        @endif
                                    </td>
                                    <td>
                                        @if(isset($event->description))
                                            {!! $event->description !!}
                                        @endif
                                    </td>
                                    <td>
                                        @if(isset($event->runs_count))
                                            {{ $event->runs_count }}
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
