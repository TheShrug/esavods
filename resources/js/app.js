require('./bootstrap');
require('datatables.net-bs4');
require('datatables.net-responsive-bs4');

$(document).ready(function() {
    initializeDataTable();
});

var table;

function initializeDataTable() {
    table = $('#mainTable').DataTable({
        paging: false,
        info: false,
        responsive: {
            details: {
                display: $.fn.dataTable.Responsive.display.childRowImmediate,
                type: ''
            }
        },
        order: [],
        language: {
            search: "Search records:"
        }
    });
}


$(document).on('click', '.video-links a', function (e) {
    e.preventDefault();
    let tr = $(this).closest('tr');
    let vodSite = $(this).data('vod-site');
    let vod = $(this).data('vod');
    let row = table.row( tr );
    let tbody = $(this).closest('tbody');
    let trs = tbody.find('tr');

    if (row.child.isShown() && tr.hasClass('shown')) {
        row.child.hide();
        tr.removeClass('shown');
        table.draw();
    }
    else if(row.child.isShown() && !tr.hasClass('shown')) {
        trs.each(function() {
           $(this).removeClass('shown');
        });
        table.draw();
        $(row.child()).find('td').append(format(row.data(), vodSite));
        tr.addClass('shown');
        if(vodSite === 'youtube') {
            initializeYoutubeVideo(vod)
        } else if(vodSite === 'twitch') {
            initializeTwitchVideo(vod)
        }
    }
    else {
        trs.each(function() {
            $(this).removeClass('shown');
        });
        table.draw();
        row.child( format(row.data(), vodSite) ).show();
        $(row.child()).addClass('child');
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
    vod = vod.toString();
    let time = 0;
    let videoId = vod;
    let hasTime = false;

    if(vod.indexOf('?t=') > -1) {
        hasTime = true;
    }

    if(hasTime) {
        time = twitchTimeStringToSeconds(vod.slice(vod.indexOf('?t=') + 3));
        videoId = vod.slice(0, vod.indexOf('?t='));
    }

    let twitchOptions = {
        height: 360,
        width: 640,
        video: videoId
    };

    let player = new Twitch.Player('videoPlayer', twitchOptions);
    player.addEventListener(Twitch.Player.READY, () => {
        /**
         * this is really unfortunate, even though the player should be ready
         * to take commands, we still have to wait a period of time to tell
         * the player to seek to a time
         */
        if(hasTime) {
            setTimeout(function(){
                player.seek(time);
            }, 5000);
        }
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
