$(document).ready(function() {
    var pages_number = parseInt($('#pages_number').val());
    var current_page = 1;

    $('#scrollpagination').attr('pagination', 'enabled');
    $('#loading').hide();
    $('#no-more-result').hide();

    $(window).on('scroll', function() {
        var scrollHeight = $(document).height();
        var scrollPos = $(window).height() + $(window).scrollTop();

        if(((scrollHeight - 300) >= scrollPos) / scrollHeight == 0) {
            if (current_page < pages_number) {
                if ($('#scrollpagination').attr('pagination') == 'enabled') {
                    current_page += 1;
                    $.ajax({
                        type: 'GET',
                        url: '/shop',
                        data: {
                            'ppg': 9,
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
