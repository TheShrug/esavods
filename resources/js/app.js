
/**
 * First we will load all of this project's JavaScript dependencies which
 * includes Vue and other libraries. It is a great starting point when
 * building robust, powerful web applications using Vue and Laravel.
 */

require('./bootstrap');
require('datatables.net-bs4');
require('datatables.net-responsive-bs4');

var table = $('.mainDataTable').DataTable({
    paging: false,
    responsive: {
        details: {
            type: 'inline',
            display: $.fn.dataTable.Responsive.display.childRowImmediate
        }
    },
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

$(document).on('click', '.expand-row-button', function () {
    var tr = $(this).closest('tr');
    var row = table.row( tr );

    if ( row.child.isShown() ) {
        // This row is already open - close it
        row.child.hide();
        tr.removeClass('shown');
    }
    else {
        // Open this row
        row.child( format(row.data()) ).show();
        tr.addClass('shown');
    }
} );

/* Formatting function for row details - modify as you need */
function format ( d ) {
    console.log(d);
    // `d` is the original data object for the row
    return '<td colspan="' + d.length +'">'+
        '</td>';
}


$('.testButton').on('click', function() {
    table.responsive.recalc();
})