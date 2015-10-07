$(document).ready(function () {

    var $price_donate_min = parseInt($( "#price_donate" ).attr( "min" ),10);
    if (isNaN($price_donate_min)) $price_donate_min = 1;

    $( "form[action~='/shop/cart/update']" ).validate({
      rules: {
        price_donate: {
          required: true,
          min: $price_donate_min
        }
      }
    });

});
