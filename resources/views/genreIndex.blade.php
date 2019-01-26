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
                            <li class="breadcrumb-item active" aria-current="page">Genres</li>
                        </ol>
                    </nav>
                </div>
            </div>
            <div class="row justify-content-center">
                <div class="col-md-12">
                    @if($genres)
                        <table class="esa-table" id="mainTable" data-order="[[0,&quot;asc&quot;]]">
                            <thead>
                                <tr>
                                    <th>Genre</th>
                                    <th data-orderable="false">Description</th>
                                </tr>
                            </thead>
                            <tbody>
                            @foreach($genres as $genre)
	                            <?php /* @var $genre \App\Genre */ ?>
                                <tr data-id="{{ $genre->id }}">
                                    <td nowrap>
                                        @if(isset($genre->name) && isset($genre->slug))
                                            <a href="{{ route('genre.show', $genre->slug) }}">{{ $genre->name }}</a>
                                        @endif
                                    </td>
                                    <td>
                                        @if(isset($genre->description))
                                            {!! $genre->description !!}
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
