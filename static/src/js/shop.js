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
  if($('#bm-body').length) {
      var animation = bodymovin.loadAnimation({
        container: document.getElementById("wrapwrap"),
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: '/sitio_imagen/static/src/js/data.json'
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
    $('form#checkout_form_imagen').submit();
  });


  $(document).on('click', '.a-submit-form-xpress', function(event){
    event.preventDefault();

    $('#checkout_form_imagen').find('input#callback').val('/shop/payment');

    $('form#checkout_form_imagen').submit();
  });
});
