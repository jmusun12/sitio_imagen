/* FUNCION QUE SE LLAMARA PARA FUNCIONALIDAD RECAPTCHA */

function recaptchaDataCallback() {
    var tokenRecaptcha = grecaptcha.getResponse();

    if (tokenRecaptcha) {
        $('input[name="recaptcha"]').val(tokenRecaptcha);
    }
}

function recaptchaDataExpiredCallback() {
    $('input[name="recaptcha"]').val('');
}

function recaptchaDataErrorCallback() {
    $('input[name="recaptcha"]').val('');
}
