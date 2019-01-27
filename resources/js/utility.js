// esa 2018

let trs = $('.usertext-body.may-blank-within.md-container table tbody tr');
let runs = [];

$(trs).each(function() {
    let tds = $(this).find('td');
    let timeLink = $(tds[2]).find('a')[0];
    let time = $(timeLink).html();
    let twitchLink = $(timeLink).attr('href');
    let name = $(tds[0]).text()

    runs.push({
        name: name,
        twitch: twitchLink,
        time: time,
    })

});

console.log(JSON.stringify(runs))

// youtube
javascript: (function(e, s) {
    e.src = s;
    e.onload = function() {
        jQuery.noConflict();
        console.log('jQuery injected');
    };
    document.head.appendChild(e);
})(document.createElement('script'), '//code.jquery.com/jquery-latest.min.js')

let rows = jQuery('.yt-simple-endpoint');

let list = []
jQuery(rows).each(function() {
    let title = jQuery(this).find('#video-title').text();
    let link = jQuery(this).attr('href');
    if(title) {
        list.push({
            title: title,
            link: link
        })
    }
});

console.log(JSON.stringify(list))

// esa 2015
let trs = $('.usertext-body.may-blank-within.md-container table tbody tr');
let runs = [];

$(trs).each(function() {
    let tds = $(this).find('td');
    let timeLink = $(tds[2]).find('a')[0];
    let time = $(timeLink).text();
    let name = $(tds[0]).text();
    let players = $(tds[1]).find('a');
    console.log(players);

    let playersString = '';

    $(players).each(function() {
        if($(this).attr('href')) {
            if(playersString !== '') {
                playersString += '|';
            }
            playersString += '[' + $(this).text() +']('+ $(this).attr('href') +')';
        }
    })

    runs.push({
        name: name,
        players: playersString,
        time: time,
    })

});

console.log(JSON.stringify(runs))