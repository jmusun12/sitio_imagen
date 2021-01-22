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
      $('input[name=institucion]').css('border', '1px solid #dc3545');
      valid = false;
    } else {
      $('input[name=institucion]').css('border', '1px solid #ced4da');
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

    if( !$('#checkbox_cgv').prop('checked') ) {
        document.getElementById('err_term').innerHTML="Debe aceptar los terminos y condiciones";
        valid = false;
    }

    return valid;
  }

  $(document).ready(function() {
    $(document).on('click', '#btn-submit-kit', function(event){
        event.preventDefault();

        $('#btn-submit-kit').css('display', 'none');

        if ( validateFormKit() ) {
            $('form#form-get-kit').submit();
        } else {
            $('#btn-submit-kit').css('display', 'block');
        }
    });
  });