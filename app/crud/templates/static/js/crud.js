$(document).ready(function () {
    $('[data-toggle="offcanvas"]').click(function () {
        $('.row-offcanvas').toggleClass('active')
    });
    $('ul.list-group > li > a[href="' + document.location.pathname + '"]').parent().addClass('active');
});
