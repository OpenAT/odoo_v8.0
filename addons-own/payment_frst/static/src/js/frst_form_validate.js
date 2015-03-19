$(document).ready(function () {

    $( "#frst" ).validate({
      rules: {
        frst_iban: {
          required: true,
          iban: true
        },
        frst_bic: {
          required: true,
          bic: true
        }
      }
    });

});
