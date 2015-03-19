$(document).ready(function () {

    // CART: Hide Tax if 0
    if ( parseFloat($("#order_total_taxes span.oe_currency_value").html()) <= 0 ) {
        $( "#order_total_taxes" ).addClass( "hidden" );
    }
    // CART: Hide Delivery if 0
    if ( parseFloat($("#order_delivery span.oe_currency_value").html()) <= 0 ) {
        $( "#order_delivery" ).addClass( "hidden" );
    }

});
