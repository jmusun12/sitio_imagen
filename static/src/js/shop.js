/* JAVASCRIPT PARA MENU */
const body = document.body;
const scrollUp = "scroll-up";
const scrollDown = "scroll-down";
let lastScroll = 0;

window.addEventListener("scroll", () => {
  const currentScroll = window.pageYOffset;
  if (currentScroll <= 0) {
    body.classList.remove(scrollUp);
    return;
  }

  if (currentScroll > lastScroll && !body.classList.contains(scrollDown)) {
    // down
    body.classList.remove(scrollUp);
    body.classList.add(scrollDown);
  } else if (currentScroll < lastScroll && body.classList.contains(scrollDown)) {
    // up
    body.classList.remove(scrollDown);
    body.classList.add(scrollUp);
  }

  lastScroll = currentScroll;
});


$(document).ready(function () {
  $('[data-toggle="tooltip"]').tooltip();

  $('.slider-related-product').slick({
        dots: true,
        infinite: false,
        speed: 300,
        slidesToShow: 4,
        slidesToScroll: 4,
        responsive: [
            {
                breakpoint: 1024,
                settings: {
                  slidesToShow: 3,
                  slidesToScroll: 3,
                  infinite: true,
                  dots: true
                }
            },
            {
                breakpoint: 780,
                settings: {
                  slidesToShow: 2,
                  slidesToScroll: 2
                }
            },
            {
                breakpoint: 480,
                settings: {
                  slidesToShow: 1,
                  slidesToScroll: 1
                }
            }
        ]
    });

  $('.slider-product-cart').slick({
    dots: true,
    infinite: false,
    speed: 300,
    slidesToShow: 1,
    slidesToScroll: 1
  });

  // inicializacion de bodymovin div
  if($('#green_cloud').length) {
      var animation = bodymovin.loadAnimation({
        container: document.getElementById("wrapwrap"),
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: '/sitio_imagen/static/src/js/green_cloud/data.json'
      });
  }

  if($('#yellow_cloud').length) {
      var animation = bodymovin.loadAnimation({
        container: document.getElementById("wrapwrap"),
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: '/sitio_imagen/static/src/js/yellow_cloud/data.json'
      });
  }

  if($('#pink_cloud').length) {
      var animation = bodymovin.loadAnimation({
        container: document.getElementById("wrapwrap"),
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: '/sitio_imagen/static/src/js/pink_cloud/data.json'
      });
  }

  if($('#violet_cloud').length) {
      var animation = bodymovin.loadAnimation({
        container: document.getElementById("wrapwrap"),
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: '/sitio_imagen/static/src/js/violet_cloud/data.json'
      });
  }

  if($('#blue_cloud').length) {
      var animation = bodymovin.loadAnimation({
        container: document.getElementById("wrapwrap"),
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: '/sitio_imagen/static/src/js/blue_cloud/data.json'
      });
  }

  if($('#orange_cloud').length) {
      var animation = bodymovin.loadAnimation({
        container: document.getElementById("wrapwrap"),
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: '/sitio_imagen/static/src/js/orange_cloud/data.json'
      });
  }

/*
  $('.slider-product-images').slick({
    dots: false,
    infinite: false,
    speed: 300,
    slidesToShow: 1,
    slidesToScroll: 1,
    arrows: false,
    fade: true,
    asNavFor: '.slider-product-images-nav'
  });

  $('.slider-product-images-nav').slick({
    dots: false,
    infinite: false,
    speed: 300,
    slidesToShow: 3,
    slidesToScroll: 3,
    asNavFor: '.slider-product-images',
    focusOnSelect: true,
    variableWidth: true
  });
    */

  $(document).on('click', '.a-linea-m', function (event) {
    event.preventDefault();

    if (!$('.nav-book').hasClass('active')) {
      $('.nav-book').addClass('active');
    }
  });

  $(document).on('click', '.a-close-book', function (event) {
    event.preventDefault();

    if ($('.nav-book').hasClass('active')) {
      $('.nav-book').removeClass('active');
    }
  });

  $(document).on('click', '.a-img-linea', function(event) {
    event.preventDefault();

    if (!$('.nav-book').hasClass('active')) {
      $('.nav-book').addClass('active');
    }
  });

  $(document).on('click', '.a-img-linea-nav-hidden', function(event) {
    event.preventDefault();

    if (!$('.nav-book').hasClass('active')) {
      $('.nav-book').addClass('active');
    }
  });

  $(document).on('click', '.btn-qty-plus', function () {
    value = $('input.input-qty').val();
    qty = parseInt(value);
    qty += 1

    $('input.input-qty').val(qty);
  });

  $(document).on('click', '.btn-qty-minus', function() {
    value = $('input.input-qty').val();
    qty = parseInt(value);

    if (qty == 1) {
      $('input.input-qty').val(qty);
    } else {
      qty -= 1;
      $('input.input-qty').val(qty);
    }
  });


  // click a boton de siguiente paso en proceso de pago
  /*$(document).on('click', '.btn-next-step', function (event) {
    event.preventDefault();
    var currentCollapse = $(this).attr('current-controls');
    var nextControl = $(this).attr('href');

    $(currentCollapse).collapse('toggle');
    $(nextControl).focus();
  });*/

  // envio de formulario para agregar al carrito

/*
  $(document).on('click', '.a-submit', function (event) {
    event.preventDefault();
    var $target = event.target;

    $form = $target.parent('form.form-add-cart');

    $form.submit();
  });
  */

  $(document).on('click', '.related-a-add-cart', function (event) {
    event.preventDefault();

    $('form.related-form-add-cart').submit();
  });

  $(document).on('click', '.a-submit-add-address', function(event) {
    event.preventDefault();

    $('.form-add-address').submit();
  });

  $(document).on('click', '.a-submit-form-checkout', function(event) {
    event.preventDefault();

    $('#checkout_form_imagen').find('input#callback').val('/shop/checkout');

    if ( validateFormAddress() ) {
      console.log('Valido');
      $('form#checkout_form_imagen').submit();
    } else {
      console.log('No Valido');
    }
  });


  $(document).on('click', '.a-submit-form-xpress', function(event){
    event.preventDefault();

    $('#checkout_form_imagen').find('input#callback').val('/shop/payment');

    if ( validateFormAddress() ) {
      console.log('Valido');
      $('form#checkout_form_imagen').submit();
    } else {
      console.log('No Valido');
    }
  });


  function validateFormAddress() {
    valid = true;
    
    let name = $('input[name=name]').val();
    if ( name == null || name === '') {
      $('input[name=name]').css('border', '1px solid #dc3545');
      valid = false;
    } else {
      $('input[name=name]').css('border', '1px solid #ced4da');
    }

    let email = $('input[name=email]').val();
    if ( email == null || email === '' ) {
      $('input[name=email]').css('border', '1px solid #dc3545');
      valid = false;
    } else {
      $('input[name=name]').css('border', '1px solid #ced4da');
    }

    let phone = $('input[name=phone]').val();
    if ( phone == null || phone === '') {
      $('input[name=phone]').css('border', '1px solid #dc3545');
      valid = false;
    } else {
      $('input[name=name]').css('border', '1px solid #ced4da');
    }

    let street = $('input[name=street]').val();
    if ( street == null || street === '') {
      $('input[name=street]').css('border', '1px solid #dc3545');
      valid = false;
    } else {
      $('input[name=name]').css('border', '1px solid #ced4da');
    }

    let city = $('input[name=city]').val();
    if ( city == null || city === '') {
      $('input[name=city]').css('border', '1px solid #dc3545');
      valid = false;
    } else {
      $('input[name=name]').css('border', '1px solid #ced4da');
    }

    // let zip = $('input[name=zip]').val();
    // if ( zip == null || zip === '') {
    //   $('input[name=zip]').css('border', '1px solid #dc3545');
    //   valid = false;
    // } else {
    //   $('input[name=name]').css('border', '1px solid #ced4da');
    // }

    let country_id = $('select[name=country_id]').val();
    if ( country_id == null || country_id === '') {
      $('select[name=country_id]').css('border', '1px solid #dc3545');
      valid = false;
    } else {
      $('select[name=name]').css('border', '1px solid #ced4da');
    }

    let state_id = $('select[name=state_id]').val();
    if ( state_id == null || state_id === '') {
      $('select[name=state_id]').css('border', '1px solid #dc3545');
      valid = false;
    } else {
      $('select[name=name]').css('border', '1px solid #ced4da');
    }

    var recaptcha = $("#g-recaptcha-response").val();
    if (recaptcha === "") {
      document.getElementById('err').innerHTML="Complete el campo 'No soy un robot'";
      valid = false;
    }

    return valid; 
  }


  $(document).on('click', '.show_coupon_imagen', function( event ) {
    event.preventDefault();
    
    $('.coupon_form').removeClass('d-none');
  });

  // $(document).on('click', '.submit-control', function(event){
  //   event.preventDefault();

  //   var recaptcha = $("#g-recaptcha-response").val();
  //   if (recaptcha === "") {
  //     document.getElementById('err').innerHTML="Complete el campo 'No soy un robot'";      
  //   } else {
  //       $('form#form-payment').submit();
  //   }
  // });

  $(document).on('click', '.a-submit-cupon', function(event) { 
    event.preventDefault();

    let code = $('input[name=promo]').val();

    if ( code == null || code === '' ) {
      document.getElementById('err').innerHTML="Código de promoción requerido.";
    } else {
      $('form[name=coupon_code]').submit();
    }
  });

  $(document).on('click', '.a-submit-confirm', function(event) { 
    event.preventDefault();
    $('form#form-payment-validate').submit();
  });
});
