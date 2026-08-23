import $ from 'jquery';

/*
 | This module exists rather than living at the top of app.js because ES module
 | imports are hoisted: everything app.js imports is evaluated before app.js's
 | own body runs. Bootstrap's jQuery plugin and DataTables' UMD wrapper both
 | want jQuery in place first, so the global assignment has to happen inside an
 | imported module — app.js imports this one ahead of them.
 */
window.$ = window.jQuery = $;

export default $;
