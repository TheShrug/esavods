
/**
 * First we will load all of this project's JavaScript dependencies which
 * includes Vue and other libraries. It is a great starting point when
 * building robust, powerful web applications using Vue and Laravel.
 */

require('./bootstrap');
require('datatables.net-bs4');
require('datatables.net-responsive-bs4');

var table = $('#mainTable').DataTable({
    paging: false,
    responsive: true,
    order: [],
    columns: [

        { orderable: true },
        { orderable: true },
        { orderable: true },
        { orderable: true },
        { orderable: true },
        { orderable: true },
        { orderable: false, searchable: false },
    ]
});

$(document).on('click', '.video-links a', function (e) {
    e.preventDefault();
    let tr = $(this).closest('tr');
    let vodSite = $(this).data('vod-site');
    let vod = $(this).data('vod');
    let row = table.row( tr );


    if ( row.child.isShown() ) {
        // This row is already open - close it
        row.child.hide();
        tr.removeClass('shown');
    }
    else {
        // Open this row
        row.child( format(row.data(), vodSite) ).show();
        tr.addClass('shown');

        if(vodSite === 'youtube') {
            initializeYoutubeVideo(vod)
        } else if(vodSite === 'twitch') {
            initializeTwitchVideo(vod)
        }

    }
} );


function initializeYoutubeVideo(vod) {
    let time = vod.slice(vod.indexOf('?t=') + 3)
    let player = new YT.Player('videoPlayer', {
        height: '360',
        width: '640',
        videoId: vod,
        playerVars: {
            start: time
        },
        events: {
            'onReady': function(event) {
                event.target.seekTo(time);
                event.target.playVideo();
            }
        }
    });
}

function initializeTwitchVideo(vod) {
    let time = twitchTimeStringToSeconds(vod.slice(vod.indexOf('?t=') + 3));
    let videoId = vod.slice(0, vod.indexOf('?t='));
    let twitchOptions = {
        height: 360,
        width: 640,
        video: videoId
    }

    let player = new Twitch.Player('videoPlayer', twitchOptions);
    player.addEventListener(Twitch.Player.READY, () => {
        /**
         * this is really unfortunate, even though the player should be ready
         * to take commands, we still have to wait a period of time to tell
         * the player to seek to a time
         */
        setTimeout(function(){
            player.seek(time);
        }, 5000);
    });
}

function twitchTimeStringToSeconds(time) {
    let hours = (time.indexOf('h') !== -1) ? parseInt(time.slice(0, time.indexOf('h'))) : 0;
    let minutes = (time.indexOf('m') !== -1) ? parseInt(time.slice(time.indexOf('m') - 2, time.indexOf('m'))) : 0;
    let seconds = (time.indexOf('s') !== -1) ? parseInt(time.slice(time.indexOf('s') - 2, time.indexOf('s'))) : 0;

    return (hours * 60 * 60) + (minutes * 60) + seconds;
}

/* Formatting function for row details */
function format (d, vodSite) {
    let format = '';

    if(vodSite === 'youtube') {
        format = '<div class="embed-responsive embed-responsive-16by9">'+
            '<div id="videoPlayer"></div>'+
            '</div>';
    } else if (vodSite === 'twitch') {
        format = '<div id="videoPlayer" class="embed-responsive embed-responsive-16by9"></div>';
    } else {
        format = '<div id="videoPlayer"></div>';
    }

    return format;
}
