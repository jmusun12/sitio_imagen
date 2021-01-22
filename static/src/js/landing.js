  function validateFormKit() {
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
      $('input[name=email]').css('border', '1px solid #ced4da');
    }

    let institucion = $('input[name=institucion]').val();
    if ( institucion == null || institucion === '') {
      $('input[name=institucion]').css('border', '1px solid #dc3545 !important');
      valid = false;
    } else {
      $('input[name=institucion]').css('border', '1px solid #ced4da !important');
    }

    let nivel = $('input[name=nivel]').val();
    if ( nivel == null || nivel === '') {
      $('input[name=nivel]').css('border', '1px solid #dc3545 !important');
      valid = false;
    } else {
      $('input[name=nivel]').css('border', '1px solid #ced4da !important');
    }

    let recaptcha = $("#g-recaptcha-response").val();
    if (recaptcha === "") {
      document.getElementById('err').innerHTML="Complete el campo 'No soy un robot'";
      valid = false;
    }

    return valid;
  }

  $(document).ready(function() {
    $(document).on('click', '#btn-submit-kit', function(event){
        event.preventDefault();

        if ( validateFormKit() ) {
            let email = $('input[name=email]').val();
            let url_validate_email = 'https://app.verify-email.org/api/v1/47McjgovmWIEhPyNb1GeTaMtn2cE2QsY4jef0VFIrZtZoWMSSr/verify/' + email

            $.get(url_validate_email, (data) => {
                if ( data.status === 1 ) {
                    console.log('Email válido.');
                    $('form#form-get-kit').submit();
                } else {
                    $('#msg-error-email').innerHtml = 'El correo electrónico es inválido.';
                    $('#msg-error-email').css('color', 'red');
                }
            });
        }
    });
  });