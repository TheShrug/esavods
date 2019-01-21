
/**
 * First we will load all of this project's JavaScript dependencies which
 * includes Vue and other libraries. It is a great starting point when
 * building robust, powerful web applications using Vue and Laravel.
 */

require('./bootstrap');
require('datatables.net-bs4');
require('datatables.net-responsive-bs4');

var table = $('.mainDataTable').DataTable({
    responsive: {
        details: {
            type: 'inline',
            display: $.fn.dataTable.Responsive.display.childRowImmediate
        }
    },
    order: [],
    columns: [
        { orderable: false, searchable: false },
        { orderable: true },
        { orderable: true },
        { orderable: true },
        { orderable: true },
        { orderable: true },
        { orderable: true },
        { orderable: false, searchable: false },
    ]
});

$('.testButton').on('click', function() {
    table.responsive.recalc();
})