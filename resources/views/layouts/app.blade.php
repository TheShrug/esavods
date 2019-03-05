<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
<head>
    <script async src="https://www.googletagmanager.com/gtag/js?id=UA-133310880-1"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());

        gtag('config', 'UA-133310880-1');
    </script>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="Content-Language" content="en">

    <link rel="apple-touch-icon" sizes="57x57" href="{{ asset('images/apple-icon-57x57.png') }}">
    <link rel="apple-touch-icon" sizes="60x60" href="{{ asset('images/apple-icon-60x60.png') }}">
    <link rel="apple-touch-icon" sizes="72x72" href="{{ asset('images/apple-icon-72x72.png') }}">
    <link rel="apple-touch-icon" sizes="76x76" href="{{ asset('images/apple-icon-76x76.pn') }}g">
    <link rel="apple-touch-icon" sizes="114x114" href="{{ asset('images/apple-icon-114x114.png') }}">
    <link rel="apple-touch-icon" sizes="120x120" href="{{ asset('images/apple-icon-120x120.png') }}">
    <link rel="apple-touch-icon" sizes="144x144" href="{{ asset('images/apple-icon-144x144.png') }}">
    <link rel="apple-touch-icon" sizes="152x152" href="{{ asset('images/apple-icon-152x152.png') }}">
    <link rel="apple-touch-icon" sizes="180x180" href="{{ asset('images/apple-icon-180x180.png') }}">
    <link rel="icon" type="image/png" sizes="192x192"  href="{{ asset('images/android-icon-192x192.pn') }}g">
    <link rel="icon" type="image/png" sizes="32x32" href="{{ asset('images/favicon-32x32.png') }}">
    <link rel="icon" type="image/png" sizes="96x96" href="{{ asset('images/favicon-96x96.png') }}">
    <link rel="icon" type="image/png" sizes="16x16" href="{{ asset('images/favicon-16x16.png') }}">
    <link rel="manifest" href="{{ asset('images/manifest.json') }}">
    <meta name="msapplication-TileColor" content="#ffffff">
    <meta name="msapplication-TileImage" content="{{ asset('images/ms-icon-144x144.png') }}">
    <meta name="theme-color" content="#ffffff">

    <!-- CSRF Token -->
    <meta name="csrf-token" content="{{ csrf_token() }}">

    <title>@yield('title') - ESA Vods</title>
    <meta name="description" content="@yield('description')">

    <!-- Styles -->
    <link href="{{ asset('css/app.css') }}" rel="stylesheet">
</head>
<body class="bg-primary">
    <div id="app">
        <nav class="navbar navbar-expand-md navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="{{ url('/') }}">
                    {{ config('app.name', 'Laravel') }}
                </a>
                <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="{{ __('Toggle navigation') }}">
                    <span class="navbar-toggler-icon"></span>
                </button>

                <div class="collapse navbar-collapse" id="navbarSupportedContent">
                    <ul class="navbar-nav mr-auto">
                        <li class="nav-item dropdown">
                            <a id="navbarDropdown" class="nav-link dropdown-toggle" href="#" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" v-pre>
                                Events <span class="caret"></span>
                            </a>
                            <div class="dropdown-menu double" aria-labelledby="navbarDropdown">
                                <h6><a href="{{ route('events') }}" class="dropdown-item dropdown-header">All Events</a></h6>
                                <?php $chunks = $menu['events']->chunk(ceil(count($menu['events']) / 2)); ?>
                                <div class="container-fluid">
                                    <div class="row">
                                        @foreach($chunks as $chunk)
                                            <div class="col-6 px-0">
                                                @foreach($chunk as $event)
                                                    <a class="dropdown-item" href="{{ route('event.show', $event->slug) }}">
                                                        {{ $event->name }}
                                                    </a>
                                                @endforeach
                                            </div>
                                        @endforeach
                                    </div>
                                </div>
                            </div>
                        </li>
                        <li class="nav-item dropdown">
                            <a id="navbarDropdown" class="nav-link dropdown-toggle" href="#" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" v-pre>
                                Platforms <span class="caret"></span>
                            </a>
                            <div class="dropdown-menu triple" aria-labelledby="navbarDropdown">
                                <h6><a href="{{ route('platforms') }}" class="dropdown-item dropdown-header">All Platforms</a></h6>

	                            <?php $chunks = $menu['platforms']->chunk(ceil(count($menu['platforms']) / 3)); ?>
                                <div class="container-fluid">
                                    <div class="row">
                                        @foreach($chunks as $chunk)
                                            <div class="col-4 px-0">
                                                @foreach($chunk as $platform)
                                                    <a class="dropdown-item" href="{{ route('platform.show', $platform->slug) }}">
                                                        {{ $platform->name }}
                                                    </a>
                                                @endforeach
                                            </div>
                                        @endforeach
                                    </div>
                                </div>



                            </div>
                        </li>
                        {{--<li class="nav-item dropdown">--}}
                            {{--<a id="navbarDropdown" class="nav-link dropdown-toggle" href="#" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" v-pre>--}}
                                {{--Genres <span class="caret"></span>--}}
                            {{--</a>--}}
                            {{--<div class="dropdown-menu" aria-labelledby="navbarDropdown">--}}
                                {{--<h6><a href="{{ route('genres') }}" class="dropdown-item dropdown-header">All Genres</a></h6>--}}
                                {{--@if(isset($menu['genres']))--}}
                                    {{--@foreach($menu['genres'] as $genre)--}}
                                        {{--<a class="dropdown-item" href="{{ route('genre.show', $genre->slug) }}">--}}
                                            {{--{{ $genre->name }}--}}
                                        {{--</a>--}}
                                    {{--@endforeach--}}
                                {{--@endif--}}
                            {{--</div>--}}
                        {{--</li>--}}
                        <li class="nav-item dropdown">
                            <a id="navbarDropdown" class="nav-link dropdown-toggle" href="#" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" v-pre>
                                Categories <span class="caret"></span>
                            </a>
                            <div class="dropdown-menu" aria-labelledby="navbarDropdown">
                                <h6><a href="{{ route('categories') }}" class="dropdown-item dropdown-header">All Categories</a></h6>
                                @if(isset($menu['categories']))
                                    @foreach($menu['categories'] as $category)
                                        <a class="dropdown-item" href="{{ route('category.show', $category->slug) }}">
                                            {{ $category->name }}
                                        </a>
                                    @endforeach
                                @endif
                            </div>
                        </li>
                    </ul>
                    @auth
                        <ul class="navbar-nav ml-auto">
                            <li class="nav-item dropdown">
                                <a id="navbarDropdown" class="nav-link dropdown-toggle" href="#" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" v-pre>
                                    {{ Auth::user()->name }} <span class="caret"></span>
                                </a>
                                <div class="dropdown-menu dropdown-menu-right" aria-labelledby="navbarDropdown">
                                    <a class="dropdown-item" href="/dashboard">
                                        {{ __('Dashboard') }}
                                    </a>
                                    <a class="dropdown-item" href="{{ route('logout') }}"
                                       onclick="event.preventDefault();
                                                         document.getElementById('logout-form').submit();">
                                        {{ __('Logout') }}
                                    </a>
                                    <form id="logout-form" action="{{ route('logout') }}" method="POST" style="display: none;">
                                        @csrf
                                    </form>
                                </div>
                            </li>
                        </ul>
                    @endauth
                </div>
            </div>
        </nav>
        <main>
            @yield('content')
        </main>
        <footer class="bg-primary">
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-md-12">
                    <p class="py-3 m-0 d-inline-block">Copyright {{ Date('Y') }} ESA Vods</p>
                    <ul class="py-3 d-inline-block">
                        {{--<li><a href="#">Made with <i class="fas fa-heart"></i></a></li>--}}
                        <li><a href="{{ route('about') }}">About</a></li>
                        <li><a href="mailto:esavods@gmail.com">esavods@gmail.com</a></li>
                    </ul>
                    </div>
                </div>
            </div>
        </footer>
    </div>
    <!-- Scripts -->
    <script src='https://www.youtube.com/iframe_api'></script>
    <script src="https://player.twitch.tv/js/embed/v1.js"></script>
    <script src="{{ asset('js/app.js') }}" defer></script>
    @if(isset($dashboard) && $dashboard == true)
        <script src="{{ asset('js/dashboard.js') }}" defer></script>
    @endif
</body>
</html>
