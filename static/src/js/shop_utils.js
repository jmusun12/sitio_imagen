odoo.define('sitio_imagen.header_imagen', function(require){
    'use strict';
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');

    publicWidget.registry.websiteShopHeader = publicWidget.Widget.extend({
        selector: '#wrapwrap',
        events: {
            'click .cart-scrollable': '_onCartTopClick',
            'click .a-cart-top-fixed': '_onCartTopFixed',
            'click .cart-other-page': '_onCartOtherPage',
            'click .cart-mobil': '_onCartMobil',
        },

        //
        // Handlers
        //
        _onCartTopClick: function(ev) {
            if ($('.nav-cart').hasClass('active')) {
                $('.nav-cart').removeClass('active')
            } else {
                var $divCart = $('.detail-cart');

                /*
                this._rpc({
                    route: '/shop/cart',
                    params: {
                        type: 'slide'
                    },
                }).then(function(data){
                    // set content template detail cart
                    $divCart.empty().append(data);
                    $('.nav-cart').addClass('active');
                });
                */

                $.get("/shop/cart", {
                    type: 'slide',
                }).then(function (data) {
                    // set content template detail cart
                    $divCart.empty().append(data);
                    $('.nav-cart').addClass('active');
                });
            }
        },

        _onCartTopFixed: function(ev) {
            if ($('.nav-cart').hasClass('active')) {
                $('.nav-cart').removeClass('active')
            } else {
                var $divCart = $('.detail-cart');

                $.get("/shop/cart", {
                    type: 'slide',
                }).then(function (data) {
                    // set content template detail cart
                    $divCart.empty().append(data);
                    $('.nav-cart').addClass('active');
                });
            }
        },

        _onCartOtherPage: function(ev) {
            if ($('.nav-cart').hasClass('active')) {
                $('.nav-cart').removeClass('active')
            } else {
                var $divCart = $('.detail-cart');

                $.get("/shop/cart", {
                    type: 'slide',
                }).then(function (data) {
                    // set content template detail cart
                    $divCart.empty().append(data);
                    $('.nav-cart').addClass('active');
                });
            }
        },

        _onCartMobil: function(ev) {
            if ($('.nav-cart').hasClass('active')) {
                $('.nav-cart').removeClass('active')
            } else {
                var $divCart = $('.detail-cart');

                $.get("/shop/cart", {
                    type: 'slide',
                }).then(function (data) {
                    // set content template detail cart
                    $divCart.empty().append(data);
                    $('.nav-cart').addClass('active');
                });
            }
        },
    });
});

/*
odoo.define('sitio_imagen.address_imagen', function(require){
    'use strict';
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');

    publicWidget.registry.websiteAdressImagen = publicWidget.Widget.extend({
        selector: '#detail_sale_imagen',
        events: {
            'click .a-submit-form-checkout': '_onFormCheckout',
        },

        _onFormCheckout: function(ev) {
            ev.preventDefault();

            var $form = $('#checkout_form_imagen');
            $.post(
                $form.attr('action'),
                $form.serialize()+'&type="json_imagen"',
                function(data) {
                    var $divListAddress = $('#list_address');
                    $divListAddress.empty().append(data);
                }
            );
        },
    });
});
*/

odoo.define('sitio_imagen.cart_imagen', function(require){
    'use strict';
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');

     publicWidget.registry.websiteCartImagen = publicWidget.Widget.extend({
        selector: '#detail-cart',
        events:  {
            'change #input-quantity-line': '_onChangeQuantity',
            'click #delete_product-cart': '_onClickRemoveProduct',
        },

        _onClickRemoveProduct: function(ev) {
            ev.preventDefault();

            $('#input-quantity-line').val(0).trigger('change');
        },

        _onChangeQuantity: function(ev) {
            $('#input-quantity-line').addClass('border');
        },
     });
});

