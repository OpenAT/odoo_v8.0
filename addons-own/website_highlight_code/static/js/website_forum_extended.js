    // START: Original Java script of /website_forum/static/src/js/website_forum.js except ckeditor parts
    openerp.website.if_dom_contains('.website_forum', function () {
        $('.karma_required').on('click', function (ev) {
            var karma = $(ev.currentTarget).data('karma');
            if (karma) {
                ev.preventDefault();
                var $warning = $('<div class="alert alert-danger alert-dismissable oe_forum_alert" id="karma_alert">'+
                    '<button type="button" class="close notification_close" data-dismiss="alert" aria-hidden="true">&times;</button>'+
                    karma + ' karma is required to perform this action. You can earn karma by having '+
                            'your answers upvoted by the community.</div>');
                var vote_alert = $(ev.currentTarget).parent().find("#vote_alert");
                if (vote_alert.length == 0) {
                    $(ev.currentTarget).parent().append($warning);
                }
            }
        });

        $('.vote_up,.vote_down').not('.karma_required').on('click', function (ev) {
            ev.preventDefault();
            var $link = $(ev.currentTarget);
            openerp.jsonRpc($link.data('href'), 'call', {})
                .then(function (data) {
                    if (data['error']){
                        if (data['error'] == 'own_post'){
                            var $warning = $('<div class="alert alert-danger alert-dismissable oe_forum_alert" id="vote_alert">'+
                                '<button type="button" class="close notification_close" data-dismiss="alert" aria-hidden="true">&times;</button>'+
                                'Sorry, you cannot vote for your own posts'+
                                '</div>');
                        } else if (data['error'] == 'anonymous_user'){
                            var $warning = $('<div class="alert alert-danger alert-dismissable oe_forum_alert" id="vote_alert">'+
                                '<button type="button" class="close notification_close" data-dismiss="alert" aria-hidden="true">&times;</button>'+
                                'Sorry you must be logged to vote'+
                                '</div>');
                        }
                        vote_alert = $link.parent().find("#vote_alert");
                        if (vote_alert.length == 0) {
                            $link.parent().append($warning);
                        }
                    } else {
                        $link.parent().find("#vote_count").html(data['vote_count']);
                        if (data['user_vote'] == 0) {
                            $link.parent().find(".text-success").removeClass("text-success");
                            $link.parent().find(".text-warning").removeClass("text-warning");
                        } else {
                            if (data['user_vote'] == 1) {
                                $link.addClass("text-success");
                            } else {
                                $link.addClass("text-warning");
                            }
                        }
                    }
                });
        });

        $('.accept_answer').not('.karma_required').on('click', function (ev) {
            ev.preventDefault();
            var $link = $(ev.currentTarget);
            openerp.jsonRpc($link.data('href'), 'call', {}).then(function (data) {
                if (data['error']) {
                    if (data['error'] == 'anonymous_user') {
                        var $warning = $('<div class="alert alert-danger alert-dismissable" id="correct_answer_alert" style="position:absolute; margin-top: -30px; margin-left: 90px;">'+
                            '<button type="button" class="close notification_close" data-dismiss="alert" aria-hidden="true">&times;</button>'+
                            'Sorry, anonymous users cannot choose correct answer.'+
                            '</div>');
                    }
                    correct_answer_alert = $link.parent().find("#correct_answer_alert");
                    if (correct_answer_alert.length == 0) {
                        $link.parent().append($warning);
                    }
                } else {
                    if (data) {
                        $link.addClass("oe_answer_true").removeClass('oe_answer_false');
                    } else {
                        $link.removeClass("oe_answer_true").addClass('oe_answer_false');
                    }
                }
            });
        });

        $('.favourite_question').on('click', function (ev) {
            ev.preventDefault();
            var $link = $(ev.currentTarget);
            openerp.jsonRpc($link.data('href'), 'call', {}).then(function (data) {
                if (data) {
                    $link.addClass("forum_favourite_question")
                } else {
                    $link.removeClass("forum_favourite_question")
                }
            });
        });

        $('.comment_delete').on('click', function (ev) {
            ev.preventDefault();
            var $link = $(ev.currentTarget);
            openerp.jsonRpc($link.parent('form').attr('action'), 'call', {}).then(function (data) {
                $link.parents('.comment').first().remove();
            });
        });

        $('.notification_close').on('click', function (ev) {
            ev.preventDefault();
            var $link = $(ev.currentTarget);
            openerp.jsonRpc("/forum/notification_read", 'call', {
                'notification_id': $link.attr("id")});
        });

        $('.send_validation_email').on('click', function (ev) {
            ev.preventDefault();
            var $link = $(ev.currentTarget);
            openerp.jsonRpc("/forum/send_validation_email", 'call', {
                'forum_id': $link.attr('forum-id'),
            }).then(function (data) {
                if (data) {
                    $('button.validation_email_close').click();
                }
            });
        });

        $('.validated_email_close').on('click', function (ev) {
            openerp.jsonRpc("/forum/validate_email/close", 'call', {});
        });


        $('input.js_select2').select2({
            tags: true,
            tokenSeparators: [",", " ", "_"],
            maximumInputLength: 35,
            minimumInputLength: 2,
            maximumSelectionSize: 5,
            lastsearch: [],
            createSearchChoice: function (term) {
                if ($(lastsearch).filter(function () { return this.text.localeCompare(term) === 0;}).length === 0) {
                    //check Karma
                    if (parseInt($("#karma").val()) >= parseInt($("#karma_retag").val())) {
                        return {
                            id: "_" + $.trim(term),
                            text: $.trim(term) + ' *',
                            isNew: true,
                        };
                    }

                }
            },
            formatResult: function(term) {
                if (term.isNew) {
                    return '<span class="label label-primary">New</span> ' + _.escape(term.text);
                }
                else {
                    return _.escape(term.text);
                }
            },
            ajax: {
                url: '/forum/get_tags',
                dataType: 'json',
                data: function(term, page) {
                    return {
                        q: term,
                        t: 'select2',
                        l: 50
                    };
                },
                results: function(data, page) {
                    var ret = [];
                    _.each(data, function(x) {
                        ret.push({ id: x.id, text: x.name, isNew: false });
                    });
                    lastsearch = ret;
                    return { results: ret };
                }
            },

            // Take default tags from the input value
            initSelection: function (element, callback) {
                var data = [];
                _.each(element.data('init-value'), function(x) {
                    data.push({ id: x.id, text: x.name, isNew: false });
                });
                element.val('');
                callback(data);
            },
        });

        if($('input.load_tags').length){
            var tags = $("input.load_tags").val();
            $("input.load_tags").val("");
            set_tags(tags);
        };

        function set_tags(tags) {
            $("input.load_tags").textext({
                plugins: 'tags focus autocomplete ajax',
                tagsItems: tags.split(","),
                //Note: The following list of keyboard keys is added. All entries are default except {32 : 'whitespace!'}.
                keys: {8: 'backspace', 9: 'tab', 13: 'enter!', 27: 'escape!', 37: 'left', 38: 'up!', 39: 'right',
                    40: 'down!', 46: 'delete', 108: 'numpadEnter', 32: 'whitespace!'},
                ajax: {
                    url: '/forum/get_tags',
                    dataType: 'json',
                    cacheResults: true
                }
            });
            // Adds: create tags on space + blur
            $("input.load_tags").on('whitespaceKeyDown blur', function () {
                $(this).textext()[0].tags().addTags([ $(this).val() ]);
                $(this).val("");
            });
            $("input.load_tags").on('isTagAllowed', function(e, data) {
                if (_.indexOf($(this).textext()[0].tags()._formData, data.tag) != -1) {
                    data.result = false;
                }
            });
        }
    });
    // END: Original Java script of /website_forum/static/src/js/website_forum.js except ckeditor parts

    function website_forum_IsKarmaValid(eventNumber, minKarma){
        "use strict";
        if(parseInt($("#karma").val()) >= minKarma){
            CKEDITOR.tools.callFunction(eventNumber, this);
            return false;
        } else {
            alert("Sorry you need more than " + minKarma + " Karma.");
        }
    }

    // Wait until DOM is loaded then check if it is a .website_forum page and of test CKEDITOR and load it if needed
    // HINT: Loading of CKEDITOR is only needed if a portal user is logged in or no user is logged in at all
    $( document ).ready(function() {
        openerp.website.if_dom_contains('.website_forum', function () {

            function configureCKforForum() {
                if ($('textarea.load_editor').length) {
                    CKEDITOR.plugins.addExternal('pbckcode', '/website_highlight_code/static/lib/ckeditor_plugins/pbckcode/', 'plugin.js');
                    CKEDITOR.plugins.addExternal('maximize', '/website_highlight_code/static/lib/ckeditor_plugins/maximize/', 'plugin.js');
                    CKEDITOR.config.extraAllowedContent = 'pre(*){*}[*]; code(*){*}[*];';
                    CKEDITOR.config.height = 400;
                    CKEDITOR.document.appendStyleSheet('/website_highlight_code/static/css/ace.css');

                    textareaname = $('textarea.load_editor').attr('name');
                    CKEDITOR.replace(textareaname, {customConfig: '/website_highlight_code/static/js/config.js'});
                    if (textareaname == 'content') {
                        CKEDITOR.instances[textareaname].on('instanceReady', CKEDITORLoadComplete);
                    }

                    function CKEDITORLoadComplete() {
                        "use strict";
                        //console.log('inside CKEDITORLoadComplete');
                        $('.cke_button__link').attr('onclick', 'website_forum_IsKarmaValid(121,30)');
                        $('.cke_button__unlink').attr('onclick', 'website_forum_IsKarmaValid(125,30)');
                        $('.cke_button__image').attr('onclick', 'website_forum_IsKarmaValid(133,30)');
                    }
                }
            }

            // Load CKEDITOR if needed and start its configuration in the callback function
            // HINT: we load configureCKforForum in the callback function of getScript to make sure ckeditor.js
            //       and all needed parts are fully loaded
            if (typeof CKEDITOR === 'undefined') {
                path = window.location.protocol + '//' + window.location.host;
                $.getScript( path + "/web/static/lib/ckeditor/ckeditor.js", function( ) {
                    $.getScript( path + "/web/static/lib/ckeditor/lang/en.js", function( ) {
                        $.getScript( path + "/web/static/lib/ckeditor/styles.js", function( ) {
                            configureCKforForum();
                        });
                    });
                });

            } else {
                configureCKforForum();
            }

        });
    });