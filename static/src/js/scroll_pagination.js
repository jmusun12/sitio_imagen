$(document).ready(function() {
    var pages_number = parseInt($('#pages_number').val());
    var current_page = 1;

    $('#scrollpagination').attr('pagination', 'enabled');
    $('#loading').hide();
    $('#no-more-result').hide();
    var url_get = $('#url_get').val();

    function getDocumentHeight() {
        const body = document.body;
        const html = document.documentElement;

        return Math.max(
            body.scrollHeight, body.offsetHeight,
            html.clientHeight, html.scrollHeight, html.offsetHeight
        );
    };

    function getScrollTop() {
        return (window.pageYOffset !== undefined) ? window.pageYOffset : (document.documentElement || document.body.parentNode || document.body).scrollTop;
    }

    $(window).on('scroll', function() {
        var scrollHeight = $(document).height();
        var scrollPos = $(window).height() + $(window).scrollTop();

        // if (getScrollTop() < getDocumentHeight() - window.innerHeight) return;
        // if(((scrollHeight - 300) >= scrollPos) / scrollHeight == 0) {
        if(((scrollHeight - 500) >= scrollPos) / scrollHeight == 0) {
            if (current_page < pages_number) {
                if ($('#scrollpagination').attr('pagination') == 'enabled') {
                    current_page += 1;
                    $.ajax({
                        type: 'GET',
                        url: url_get,
                        data: {
                            'ppg': 12,
                            'page': current_page,
                            'xhr': 1
                        },
                        success: function(data) {
                            if (data != null) {
                                $('#list-products').append(data);
                                if (current_page > pages_number) {
                                    $('#scrollpagination').attr('pagination', 'disabled');
                                }
                            }
                        },
                        beforeSend: function() {
                            $('#loading').show();
                        },
                        complete: function() {
                            $('#loading').hide();
                        },
                        error: function() {

                        }
                    });
                }
            }
        }
    });
});
