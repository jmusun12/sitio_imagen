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
            'click #delete_product-cart': '_onClickRemoveProduct',
            'click #a-minus-qty': '_onClickMinusQty',
            'click #a-plus-qty': '_onClickPlusQty'
        },

        _onClickRemoveProduct: function(ev) {
            ev.preventDefault();

            var $input = $(ev.currentTarget).parents('div.item-product-cart').find('input#input-quantity-line');
            var product= $input.data('product-id');
            var line_id = $input.data('line-id');
            // var qty = $('#input-quantity-line').val();

            this._rpc({
                route: "/shop/cart/update_json",
                params: {
                    line_id: line_id,
                    product_id: product,
                    set_qty: 0
                },
            }).then(function(data){
                return window.location = '/shop/cart';
            });
        },

        _onClickMinusQty: function(ev) {
            ev.preventDefault();

            var $input = $(ev.currentTarget).parents('div.control-qty').find('input#input-quantity-line');
            var product_id = $input.data('product-id');
            var line_id = $input.data('line-id');
            var qty = parseInt($input.val() || 0, 10);
            var new_qty = 0;
            if (qty > 1) {
                new_qty = qty - 1;
            } else {
                new_qty = 0;
            }

            this._rpc({
                route: "/shop/cart/update_json",
                params: {
                    line_id: line_id,
                    product_id: product_id,
                    set_qty: new_qty
                },
            }).then(function(data){
                return window.location = '/shop/cart';
            });
        },

        _onClickPlusQty: function(ev) {
            ev.preventDefault();

            var $input = $(ev.currentTarget).parents('div.control-qty').find('input#input-quantity-line');
            var product_id = $input.data('product-id');
            var line_id = $input.data('line-id');
            //var qty = $('#input-quantity-line').val();

            this._rpc({
                route: "/shop/cart/update_json",
                params: {
                    line_id: line_id,
                    product_id: product_id,
                    add_qty: 1
                },
            }).then(function(data){
                return window.location = '/shop/cart';
            });
        }
     });
});

