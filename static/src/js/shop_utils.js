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

            var $input = $(ev.currentTarget).parents('div.item-product-cart').find('input.quantity-line');
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

odoo.define('sitio_imagen.product_imagen', function(require){
    'use strict';
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');

    publicWidget.registry.websiteProductImagen = publicWidget.Widget.extend({
        selector: '.detail-product',
        events:  {
            'click #delete_product-cart': '_onClickRemoveProduct',
            'click #a-minus-qty': '_onClickMinusQty',
            'click #a-plus-qty': '_onClickPlusQty',
            'click .buy-now-website': '_onClickBuyNowWebsite',
            'click .add-cart-website': '_onClickAddCartWebsite',
        },

        init: function () {
            this._super.apply(this, arguments);
            toastr.options = {
                "closeButton": false,
                "debug": false,
                "newestOnTop": false,
                "progressBar": false,
                "positionClass": "toast-bottom-center",
                "preventDuplicates": false,
                "onclick": null,
                "showDuration": "300",
                "hideDuration": "1000",
                "timeOut": "5000",
                "extendedTimeOut": "1000",
                "showEasing": "swing",
                "hideEasing": "linear",
                "showMethod": "fadeIn",
                "hideMethod": "fadeOut"
            }
        },

        _onClickBuyNowWebsite: function(ev) {
            ev.preventDefault();
            var $form = $('form.form-add-cart');
            $form.submit();
        },

        _onClickAddCartWebsite: function(ev) {
            ev.preventDefault();

            var product_id = parseInt($('input.product_id').val());
            var qty = parseInt($('input.input-qty').val())

            if (qty <=0 ){
                qty = 1;
            }

            var variants = [];

            if ($('.variant_attribute select').length > 0) {
                var selectVariant = $('.variant_attribute select');
                var value = $selectVariant.data('value_id');
                var name = $selectVariant.data('value_name');

                var data = {
                    'name': name,
                    'value': value
                }

                variants.push(data);
            }

            $('div#loading_website').removeClass('d-none');

            this._rpc({
                route: '/shop/cart/update_json_website',
                params: {
                    product_id: product_id,
                    set_qty: qty,
                    no_variant_attribute_values: variants
                }
            }).then(function(res) {
                var current_qty = parseInt($('input.input-qty').val());
                $('div#loading_website').addClass('d-none');
                toastr.info('Producto agregado');
            }).catch(function(err) {
                console.log(err);
                $('div#loading_website').addClass('d-none');
                toastr.error('No se pudo procesar la petición');
            });
        }
    });
});

odoo.define('sitio_imagen.payment_imagen',  function(require){
    'use strict';

    var core = require('web.core');
    var publicWidget = require('web.public.widget');

    var _t = core._t;
    var concurrency = require('web.concurrency');
    var dp = new concurrency.DropPrevious();

    publicWidget.registry.paymentImagen = publicWidget.Widget.extend({
        selector: '#payment-page',
        events:  {
            'click #delivery_carrier_imagen .o_delivery_carrier_select': '_onCarrierClick',
        },

        start: function () {
            var self = this;
            var $carriers = $('#delivery_carrier_imagen input[name="delivery_type"]');
            var $payButton = $('#o_payment_form_pay');
            // Workaround to:
            // - update the amount/error on the label at first rendering
            // - prevent clicking on 'Pay Now' if the shipper rating fails
            if ($carriers.length > 0) {
                if ($carriers.filter(':checked').length === 0) {
                    $payButton.prop('disabled', true);
                    $payButton.data('disabled_reasons', $payButton.data('disabled_reasons') || {});
                    $payButton.data('disabled_reasons').carrier_selection = true;
                }
                $carriers.filter(':checked').click();
            }

            // Asynchronously retrieve every carrier price
            _.each($carriers, function (carrierInput, k) {
                self._showLoading($(carrierInput));
                self._rpc({
                    route: '/shop/carrier_rate_shipment',
                    params: {
                        'carrier_id': carrierInput.value,
                    },
                }).then(self._handleCarrierUpdateResultBadge.bind(self));
            });

            return this._super.apply(this, arguments);
        },

        _showLoading: function ($carrierInput) {
            $carrierInput.siblings('.o_wsale_delivery_badge_price').html('<span class="fa fa-spinner fa-spin"/>');
        },

        _handleCarrierUpdateResult: function (result) {
            this._handleCarrierUpdateResultBadge(result);
            var $payButton = $('#o_payment_form_pay');
            var $amountDelivery = $('#amount_delivery_imagen .monetary_field');
            var $amountUntaxed = $('#amount_untaxed_imagen .monetary_field');
            var $amountTax = $('#amount_tax_imagen .monetary_field');
            var $amountTotal = $('#amount_total_imagen .monetary_field');

            if (result.status === true) {
                $amountDelivery.html(result.new_amount_delivery);
                $amountUntaxed.html(result.new_amount_untaxed);
                $amountTax.html(result.new_amount_tax);
                $amountTotal.html(result.new_amount_total);
                $payButton.data('disabled_reasons').carrier_selection = false;
                $payButton.prop('disabled', _.contains($payButton.data('disabled_reasons'), true));
            } else {
                $amountDelivery.html(result.new_amount_delivery);
                $amountUntaxed.html(result.new_amount_untaxed);
                $amountTax.html(result.new_amount_tax);
                $amountTotal.html(result.new_amount_total);
            }
        },

         _handleCarrierUpdateResultBadge: function (result) {
            var $carrierBadge = $('#delivery_carrier_imagen input[name="delivery_type"][value=' + result.carrier_id + '] ~ .o_wsale_delivery_badge_price');

            if (result.status === true) {
                 // if free delivery (`free_over` field), show 'Free', not '$0'
                 if (result.is_free_delivery) {
                     $carrierBadge.text(_t('Free'));
                 } else {
                     $carrierBadge.html(result.new_amount_delivery);
                 }
                 $carrierBadge.removeClass('o_wsale_delivery_carrier_error');
            } else {
                $carrierBadge.addClass('o_wsale_delivery_carrier_error');
                $carrierBadge.text(result.error_message);
            }
        },

         _onCarrierClick: function (ev) {
            var $radio = $(ev.currentTarget).find('input[type="radio"]');
            this._showLoading($radio);
            $radio.prop("checked", true);
            var $payButton = $('#o_payment_form_pay');
            $payButton.prop('disabled', true);
            $payButton.data('disabled_reasons', $payButton.data('disabled_reasons') || {});
            $payButton.data('disabled_reasons').carrier_selection = true;
            dp.add(this._rpc({
                route: '/shop/update_carrier',
                params: {
                    carrier_id: $radio.val(),
                },
            })).then(this._handleCarrierUpdateResult.bind(this));
        },
    });
});

odoo.define('sitio_imagen.checkout_imagen', function(require){
    'use strict';
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');

    publicWidget.registry.CheckoutImagen = publicWidget.Widget.extend({
    selector: '#checkout-imagen',
    events: {
        'click .js_change_shipping': '_onClickChangeShipping',
        'click .js_edit_address': '_onClickEditAddress',
        'click .js_delete_product': '_onClickDeleteProduct',
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {Event} ev
     */
    _onClickChangeShipping: function (ev) {
        var $old = $('.all_shipping').find('.item-address.border.border-primary');
        $old.find('.btn-ship').toggle();
        $old.addClass('js_change_shipping');
        $old.removeClass('border border-primary');

        var $new = $(ev.currentTarget).parent('div.one_kanban').find('.item-address');
        $new.find('.btn-ship').toggle();
        $new.removeClass('js_change_shipping');
        $new.addClass('border border-primary');

        var $form = $(ev.currentTarget).parent('div.one_kanban').find('form.d-none');
        $.post($form.attr('action'), $form.serialize()+'&xhr=1');
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onClickEditAddress: function (ev) {
        ev.preventDefault();
        $(ev.currentTarget).closest('div.one_kanban').find('form.d-none').attr('action', '/shop/address').submit();
    },
    });
});

odoo.define('sitio_imagen.product_list_imagen', function(require){
    'use strict';
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');

    publicWidget.registry.ProductListImagen = publicWidget.Widget.extend({
        selector: '#page-products-imagen',
        events: {
            'click .a-submit': '_onAddCart',
        },

        _onAddCart: function(ev) {
            ev.preventDefault();

            var $form = $(ev.currentTarget).parents('div.product-link').find('form.form-add-cart');
            $form.submit();
        },
    });
});

odoo.define('sitio_imagen.form_address_imagen', function( require ) {
    'use strict';
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');

    publicWidget.registry.FormAddressImagen = publicWidget.Widget.extend({ 
        selector: '#div-country',
        events: {
            'change select[name=country_id]': '_onChangeCountry'
        },

        init: function() {
            this._changeCountry = _.debounce(this._changeCountry.bind(this), 500);
        },

        /**
         * @private
         */
        _changeCountry: function () {
            if (!$("#country_id").val()) {
                return;
            }
            this._rpc({
                route: "/shop/country_infos/" + $("#country_id").val(),
                params: {
                    mode: 'shipping',
                },
            }).then(function (data) {
                // placeholder phone_code
                //$("input[name='phone']").attr('placeholder', data.phone_code !== 0 ? '+'+ data.phone_code : '');

                // populate states and display
                var selectStates = $("select[name='state_id']");
                // dont reload state at first loading (done in qweb)
                if (selectStates.data('init')===0 || selectStates.find('option').length===1) {
                    if (data.states.length) {
                        selectStates.html('');
                        _.each(data.states, function (x) {
                            var opt = $('<option>').text(x[1])
                                .attr('value', x[0])
                                .attr('data-code', x[2]);
                            selectStates.append(opt);
                        });
                        selectStates.parent('div').show();
                    } else {
                        selectStates.val('').parent('div').hide();
                    }
                    selectStates.data('init', 0);
                } else {
                    selectStates.data('init', 0);
                }

                // manage fields order / visibility
                if (data.fields) {
                    if ($.inArray('zip', data.fields) > $.inArray('city', data.fields)){
                        $(".div_zip").before($(".div_city"));
                    } else {
                        $(".div_zip").after($(".div_city"));
                    }
                    var all_fields = ["street", "zip", "city", "country_name"]; // "state_code"];
                    _.each(all_fields, function (field) {
                        $(".checkout_autoformat .div_" + field.split('_')[0]).toggle($.inArray(field, data.fields)>=0);
                    });
                }
            });
        },
        

        /**
         * @private
         * @param {Event} ev
         */
        _onChangeCountry: function (ev) {
            if (!this.$('.checkout_autoformat').length) {
                return;
            }
            $("#country_id").css('border', 'yellowgreen');
            // this._changeCountry();
        },
    });
});