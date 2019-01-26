@extends('layouts.app')

@section('title', 'Title')
@section('description', 'Description')

@section('content')
    <section class="main">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-12">
                    @if($events)
                        <table class="esa-table" id="mainTable" data-order="[[0,&quot;asc&quot;]]">
                            <thead>
                                <tr>
                                    <th>Event</th>
                                    <th data-orderable="false">Description</th>
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
