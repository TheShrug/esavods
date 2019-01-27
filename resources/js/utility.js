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