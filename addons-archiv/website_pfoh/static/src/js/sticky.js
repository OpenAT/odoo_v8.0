//$(document).ready(function(){
 // $(window).bind('scroll', function() {
  //  var navHeight = 300; // custom nav height
   // ($(window).scrollTop() > navHeight) ? $('navbar').addClass('goToTop') : $('navbar').removeClass('goToTop');
  //});
//});

//DD SCRIPT

$(document).ready(function() {
    console.log('window-scrollTopOnload: ', $(window).scrollTop());
    if ($(window).scrollTop() > 0) {
//        $('#dd-nav').addClass('affix');
        $(".navbar-static-top").addClass("top-nav-collapse");
        console.log('first_if');
    } else {
//        $('#dd-nav').removeClass('affix');
        $(".navbar-static-top").removeClass("top-nav-collapse");
                console.log('first_fi_else');
    }
    //alert("JavaScript wird geladen");
    if(window.location.href.indexOf("detail") > -1 ||
        window.location.href.indexOf("apply") > -1 ||
        window.location.href.indexOf("login")>-1) {
//    $('#dd-nav').addClass('affix');
      $(".navbar-static-top").addClass("top-nav-collapse");
            console.log('addClassAlways');
    };


$(window).scroll(function() {
    if (window.location.href.indexOf("detail") == -1 &&
         window.location.href.indexOf("apply") == -1 &&
         window.location.href.indexOf("login") == -1) {
        //console.log('window_scrollTop>50: ', $(".navbar").offset());
//        console.log('window_offsetTop: ', $(".navbar").offsetTop());
//        console.log('window.location.href.indexOf"login": ', window.location.href.indexOf("login"));
//        console.log('window.location.href.indexOf"apply": ', window.location.href.indexOf("apply"));
//        console.log('window.location.href.indexOf"detail": ', window.location.href.indexOf("detail"));
        if ($(window).scrollTop() > 50) {
//            $('#dd-nav').addClass('affix');
            $(".navbar-static-top").addClass("top-nav-collapse");
                    console.log('scrolled DOWN');
        } else {
//            $('#dd-nav').removeClass('affix');
            $(".navbar-static-top").removeClass("top-nav-collapse");
                    console.log('SCROLLED TOP');
        }
        if (($('.navbar-toggle').css('display') == 'block') && ($('.navbar-top-collapse').hasClass('collapse in'))) {
            $('.navbar-top-collapse').collapse('hide');
        }
    }
    });
});


//var wow=new WOW({boxClass:'wow',animateClass:'animated',offset:30,mobile:false,live:true});
//wow.init();
//if(/mobile/i.test(navigator.userAgent)){document.documentElement.className+=' mobile';}
//$(window).resize(function(){resize();})