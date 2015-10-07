$(document).ready(function () {

    $( "form[action~='/shop/confirm_order']" ).validate({
      rules: {
        name: {
          required: true,
          minlength:  6
        },
        //  street in this case is company - makes no sence i know but comes from odoo
        street: {
          minlength:  6
        },
        email: {
          minlength:  6,
          email: true
        },
        phone: {
          minlength:  6,
        }
      }
    });

});
