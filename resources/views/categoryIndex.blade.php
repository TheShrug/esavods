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
                        <li class="breadcrumb-item active" aria-current="page">Categories</li>
                    </ol>
                </nav>
            </div>
        </div>
        <div class="row justify-content-center">
            <div class="col-md-12">
                @if($categories)
                    <table class="esa-table" id="mainTable" data-order="[[0,&quot;asc&quot;]]">
                        <thead>
                        <tr>
                            <th>Category</th>
                            <th data-orderable="false">Description</th>
                            <th>Number of Runs</th>
                        </tr>
                        </thead>
                        <tbody>
                        @foreach($categories as $category)
				            <?php /* @var $event \App\Category */ ?>
                            <tr data-id="{{ $category->id }}">
                                <td nowrap>
                                    @if(isset($category->name) && isset($category->slug))
                                        <a href="{{ route('category.show', $category->slug) }}">{{ $category->name }}</a>
                                    @endif
                                </td>
                                <td>
                                    @if(isset($category->description))
                                        {!! $category->description !!}
                                    @endif
                                </td>
                                <td>
                                    @if(isset($category->runs_count))
                                        {{ $category->runs_count }}
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
