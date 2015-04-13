

    // Add Extra Plugins
    CKEDITOR.timestamp='ABCDE';

    //CKEDITOR.plugins.addExternal('codemirror', '/website_highlight_code/static/lib/ckeditor_plugins/codemirror_1.10/codemirror/', 'plugin.js');

    // Preparations for pbckcode
    CKEDITOR.plugins.addExternal('pbckcode', '/website_highlight_code/static/lib/ckeditor_plugins/pbckcode/', 'plugin.js');
    CKEDITOR.config.extraAllowedContent = 'pre(*){*}[*]; ';
    CKEDITOR.document.appendStyleSheet( '/website_highlight_code/static/css/ace.css' );

    openerp.website.if_dom_contains('.website_forum', function () {

        if ($('textarea.load_editor').length) {

            var editor = CKEDITOR.instances['content'];
            editor.removeAllListeners( );
            editor.destroy();
            CKEDITOR.replace('content', { customConfig: '/website_highlight_code/static/js/config.js'} );
            CKEDITOR.instances.content.on('instanceReady', CKEDITORLoadComplete2);
        }

        function CKEDITORLoadComplete2(){
            "use strict";
            $('.cke_button__link').attr('onclick','website_forum_IsKarmaValid2(33,30)');
            $('.cke_button__unlink').attr('onclick','website_forum_IsKarmaValid2(37,30)');
            $('.cke_button__image').attr('onclick','website_forum_IsKarmaValid2(41,30)');
        }

    });

    function website_forum_IsKarmaValid2(eventNumber, minKarma){
        "use strict";
        if(parseInt($("#karma").val()) >= minKarma){
            CKEDITOR.tools.callFunction(eventNumber, this);
            return false;
        } else {
            alert("Sorry you need more than " + minKarma + " Karma.");
        }
    }

