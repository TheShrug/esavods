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