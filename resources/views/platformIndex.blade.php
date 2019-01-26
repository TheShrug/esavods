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
                            <li class="breadcrumb-item active" aria-current="page">Platforms</li>
                        </ol>
                    </nav>
                </div>
            </div>
            <div class="row justify-content-center">
                <div class="col-md-12">
                    @if($platforms)
                        <table class="esa-table" id="mainTable" data-order="[[0,&quot;asc&quot;]]">
                            <thead>
                                <tr>
                                    <th>Platform</th>
                                    <th data-orderable="false">Description</th>
                                </tr>
                            </thead>
                            <tbody>
                            @foreach($platforms as $platform)
	                            <?php /* @var $platform \App\Platform */ ?>
                                <tr data-id="{{ $platform->id }}">
                                    <td nowrap>
                                        @if(isset($platform->name) && isset($platform->slug))
                                            <a href="{{ route('platform.show', $platform->slug) }}">{{ $platform->name }}</a>
                                        @endif
                                    </td>
                                    <td>
                                        @if(isset($platform->description))
                                            {!! $platform->description !!}
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
