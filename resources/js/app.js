import '../sass/app.scss';

/*
 |----------------------------------------------------------------------------
 | esavods.com
 |----------------------------------------------------------------------------
 |
 | jQuery, Bootstrap's JS, popper.js and DataTables were deleted in esavods#78
 | and what they actually did for this site is below. The script tag is
 | `defer`red, so the DOM is parsed by the time this runs and there is no
 | ready-handler.
 |
 */

const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

/*
 | Navbar
 |
 | Two behaviours, both of them a class toggle: `data-toggle="collapse"` on the
 | toggler and `data-toggle="dropdown"` on the three nav items. The CSS decides
 | what `.show` looks like; below the breakpoint the menus are part of the
 | stacked list, above it they are absolutely positioned overlays.
 */

const toggler = document.querySelector('.navbar-toggler[data-toggle="collapse"]');
const collapseTarget = toggler && document.querySelector(toggler.dataset.target);

if (toggler && collapseTarget) {
    toggler.addEventListener('click', () => {
        const open = collapseTarget.classList.toggle('show');
        toggler.setAttribute('aria-expanded', String(open));
    });
}

const dropdownToggles = Array.from(
    document.querySelectorAll('[data-toggle="dropdown"]')
);

function closeDropdowns(except) {
    dropdownToggles.forEach((toggle) => {
        if (toggle === except) {
            return;
        }
        toggle.setAttribute('aria-expanded', 'false');
        toggle.closest('.dropdown')?.classList.remove('show');
        toggle.parentElement.querySelector('.dropdown-menu')?.classList.remove('show');
    });
}

dropdownToggles.forEach((toggle) => {
    toggle.addEventListener('click', (event) => {
        event.preventDefault();
        closeDropdowns(toggle);

        const menu = toggle.parentElement.querySelector('.dropdown-menu');
        const open = menu.classList.toggle('show');
        toggle.closest('.dropdown')?.classList.toggle('show', open);
        toggle.setAttribute('aria-expanded', String(open));
    });
});

// One listener closes whichever menu is open. A click inside a menu is a click
// on one of its links, so it is left to navigate.
document.addEventListener('click', (event) => {
    if (!event.target.closest('[data-toggle="dropdown"]')) {
        closeDropdowns();
    }
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        closeDropdowns();
    }
});

/*
 | The table
 |
 | DataTables ran with `paging: false, info: false`, so what it was providing
 | was sorting, one search box, striping, and the responsive collapse. The
 | collapse is CSS now (see app.scss); the rest is here.
 |
 | The markup contract is unchanged, so the Blade templates keep saying what
 | they said to DataTables:
 |
 |   table[data-order]      initial sort, e.g. [[0,"asc"]]; [] for none
 |   th[data-sortable=false]
 |   th[data-orderable=false]   column cannot be sorted
 |   td[data-order]         sort on this value rather than the displayed text,
 |                          which is what keeps Schedule Time chronological
 */

const table = document.getElementById('mainTable');

if (table && table.tHead && table.tBodies.length) {
    initTable(table);
}

function initTable(table) {
    const headers = Array.from(table.tHead.rows[0].cells);
    const body = table.tBodies[0];
    const rows = Array.from(body.rows);
    const sortState = { column: null, direction: 'asc' };
    let filterTerms = [];

    // Sort keys are read once. The tables are server-rendered and nothing
    // rewrites a cell, so re-reading the DOM on every comparison would only
    // buy a slower sort.
    const keys = rows.map((row) =>
        headers.map((header, index) => {
            const cell = row.cells[index];
            if (!cell) {
                return '';
            }
            return (cell.dataset.order ?? cell.textContent).trim();
        })
    );

    const searchText = rows.map((row) =>
        row.textContent.replace(/\s+/g, ' ').trim().toLowerCase()
    );

    // A column sorts numerically only when every value in it is a number —
    // "Number of Runs" and nothing else, at present. Mixed columns fall back to
    // text, which is what DataTables' type detection did.
    const numericColumns = headers.map((header, index) =>
        keys.every((key) => key[index] === '' || !Number.isNaN(Number(key[index])))
    );

    function compare(a, b, column) {
        const left = keys[a][column];
        const right = keys[b][column];

        if (numericColumns[column]) {
            return (Number(left) || 0) - (Number(right) || 0);
        }

        const l = left.toLowerCase();
        const r = right.toLowerCase();
        return l < r ? -1 : l > r ? 1 : 0;
    }

    function render() {
        closePlayer();

        const order = rows.map((row, index) => index);

        if (sortState.column !== null) {
            const sign = sortState.direction === 'asc' ? 1 : -1;
            // Index breaks ties, so equal values keep their document order in
            // both directions rather than reversing among themselves.
            order.sort(
                (a, b) => sign * compare(a, b, sortState.column) || a - b
            );
        }

        let visible = 0;
        const fragment = document.createDocumentFragment();

        order.forEach((index) => {
            const row = rows[index];
            const matches = filterTerms.every((term) =>
                searchText[index].includes(term)
            );

            row.hidden = !matches;
            row.classList.toggle('odd', matches && visible++ % 2 === 0);
            fragment.appendChild(row);
        });

        body.appendChild(fragment);

        headers.forEach((header, index) => {
            if (!header.hasAttribute('aria-sort')) {
                return;
            }
            header.setAttribute(
                'aria-sort',
                index === sortState.column
                    ? sortState.direction === 'asc'
                        ? 'ascending'
                        : 'descending'
                    : 'none'
            );
        });
    }

    headers.forEach((header, index) => {
        if (header.dataset.sortable === 'false' || header.dataset.orderable === 'false') {
            return;
        }

        // Set here rather than in the templates: without this script there is
        // nothing to click, so there should be nothing that looks clickable.
        header.setAttribute('aria-sort', 'none');
        header.tabIndex = 0;

        const sort = () => {
            sortState.direction =
                sortState.column === index && sortState.direction === 'asc'
                    ? 'desc'
                    : 'asc';
            sortState.column = index;
            render();
        };

        header.addEventListener('click', sort);
        header.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                sort();
            }
        });
    });

    const filter = document.createElement('div');
    filter.className = 'table-filter';
    const label = document.createElement('label');
    label.append('Search table:');
    const input = document.createElement('input');
    input.type = 'search';
    input.setAttribute('aria-controls', table.id);
    label.appendChild(input);
    filter.appendChild(label);
    table.parentNode.insertBefore(filter, table);

    input.addEventListener('input', () => {
        filterTerms = input.value.toLowerCase().split(/\s+/).filter(Boolean);
        render();
    });

    try {
        const initial = JSON.parse(table.dataset.order || '[]');
        if (initial.length) {
            sortState.column = initial[0][0];
            sortState.direction = initial[0][1] === 'desc' ? 'desc' : 'asc';
        }
    } catch {
        // A malformed data-order is not worth a broken table; leave it unsorted.
    }

    render();
}

/*
 | The video player
 |
 | This was a DataTables child row. Without the plugin it is what it always
 | was: a `<tr>` inserted after the run's own row, holding one player.
 */

document.addEventListener('click', (event) => {
    const link = event.target.closest('.video-links a');

    if (!link) {
        return;
    }

    event.preventDefault();

    const row = link.closest('tr');
    const vodSite = link.dataset.vodSite;
    const vod = link.dataset.vod;

    watchedRun(row.dataset.id);

    // Clicking anything in the cell while this row's player is open closes it,
    // including the close control, which carries no vod of its own.
    if (row.classList.contains('shown')) {
        closePlayer();
        return;
    }

    closePlayer();
    openPlayer(row, vodSite, vod);
});

function openPlayer(row, vodSite, vod) {
    const child = document.createElement('tr');
    child.className = 'child';
    const cell = document.createElement('td');
    cell.colSpan = row.cells.length;
    cell.innerHTML = playerMarkup(vodSite);
    child.appendChild(cell);
    row.parentNode.insertBefore(child, row.nextSibling);
    row.classList.add('shown');

    if (vodSite === 'youtube') {
        initializeYoutubeVideo(vod);
    } else if (vodSite === 'twitch') {
        initializeTwitchVideo(vod);
    }
}

function closePlayer() {
    document.querySelectorAll('tr.shown').forEach((row) => {
        row.classList.remove('shown');
    });
    document.querySelectorAll('tr.child').forEach((child) => {
        child.remove();
    });
}

/* Markup for the player row */
function playerMarkup(vodSite) {
    if (vodSite === 'youtube') {
        return '<div class="embed-responsive embed-responsive-16by9">' +
            '<div id="videoPlayer"></div>' +
            '</div>';
    }

    if (vodSite === 'twitch') {
        return '<div id="videoPlayer" class="embed-responsive embed-responsive-16by9"></div>';
    }

    return '<div id="videoPlayer"></div>';
}

function initializeYoutubeVideo(vod) {
    vod = vod.toString();
    let time = 0;
    let videoId = vod;
    let hasTime = false;

    if(vod.indexOf('?t=') > -1) {
        hasTime = true;
    }

    if(hasTime) {
        // Unlike Twitch's `1h2m3s`, the two YouTube ids that carry a timestamp
        // hold plain seconds, which is also what the IFrame API's `start`
        // wants. Anything else is dropped rather than guessed at.
        time = parseInt(vod.slice(vod.indexOf('?t=') + 3), 10);
        videoId = vod.slice(0, vod.indexOf('?t='));
        hasTime = Number.isFinite(time);
    }

    // No `start` key at all without a timestamp. `slice` on an id with no
    // `?t=` used to hand YouTube the id minus its first two characters, and an
    // explicit `start: 0` is still a claim the data does not make.
    const playerVars = {};

    if(hasTime) {
        playerVars.start = time;
    }

    let player = new YT.Player('videoPlayer', {
        height: '360',
        width: '640',
        videoId: videoId,
        playerVars: playerVars,
        events: {
            'onReady': function(event) {
                if(hasTime) {
                    event.target.seekTo(time);
                }
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

function watchedRun(id) {
    if (!id) {
        return;
    }

    fetch('/run/' + id, {
        method: 'POST',
        headers: {
            'X-CSRF-TOKEN': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
        },
    });
}
