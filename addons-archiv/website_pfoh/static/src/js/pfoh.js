$(document).ready( function() {
    $('img.pfot_img_badge-header-news').after('<img src="/website_pfoh/static/src/img/badge/news-badge.png" class="pfot_img_badge-header-after1">');
    $('img.pfot_img_badge-header-schleife').after('<img src="/website_pfoh/static/src/img/badge/Siegel.png" class="pfot_img_badge-header-after2">');
    $('img.pfot_img_badge-header-siegel').after('<img src="/website_pfoh/static/src/img/badge/Siegel_Ohne-Schleife.png" class="pfot_img_badge-header-after3">');
    $('img.pfot_img_badge-header-pate').after('<img src="/website_pfoh/static/src/img/badge/Pate_werden.png" class="pfot_img_badge-header-after4">');
//    alert("it works");

//    $('#badge-pos ul li').hover( function() { //diese funktion könnte man überlegen für change on hover .... aber das geht nicht weil der html code ja erst gespeichert werden muss

$('p').each(function(){
  if($(this).children().length == 0){
//    $(this).hide();
  }
});
        if ( $('#order_total_taxes'))
        if ( $('.pfot_img_badge-header-after1').length > 0 ) {
            var prev_img =  $('.pfot_img_badge-header-after1').prev();
            //console.log('PREV IMG: ' + prev_img.attr( 'class' ) );
             if ( prev_img.hasClass('pfot_img_badge-header-news') ) {
                console.log('match');
             }
             else {
                 //console.log('remove');
                 $('.pfot_img_badge-header-after1').remove();
             }
        }
        else if ( $('.pfot_img_badge-header-after2').length > 0 ) {
            var prev_img =  $('.pfot_img_badge-header-after2').prev();
             if ( prev_img.hasClass('pfot_img_badge-header-schleife') ) {
                console.log('match');
             }
             else {
                 //console.log('remove');
                 $('.pfot_img_badge-header-after2').remove();
             }
        }
        else if ( $('.pfot_img_badge-header-after3').length > 0 ) {
                var prev_img =  $('.pfot_img_badge-header-after3').prev();
                 if ( prev_img.hasClass('pfot_img_badge-header-siegel') ) {
                    console.log('match');
                 }
                 else {
                     //console.log('remove');
                     $('.pfot_img_badge-header-after3').remove();
                 }
            }
        else if ( $('.pfot_img_badge-header-after4').length > 0 ) {
                var prev_img =  $('.pfot_img_badge-header-after4').prev();
                 if ( prev_img.hasClass('pfot_img_badge-header-pate') ) {
                    console.log('match');
                 }
                 else {
                     //console.log('remove');
                     $('.pfot_img_badge-header-after4').remove();
                 }
            }
//    });

});