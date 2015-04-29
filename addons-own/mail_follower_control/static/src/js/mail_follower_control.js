openerp.mail_follower_control = function (session) {
	
	session.mail_followers.Followers = session.mail_followers.Followers.extend({

        /** FULL OVERWRITE: because we need to add more data to the records: 'notify_email'
         *  Do not forget to update the python function "read_followers_data" in "mail_follower_control.py"
         *  ("read_followers_data" is called by JS function "fetch_followers" which then calls "display_followers")
         *
         * */
        display_followers: function (records) {
            var self = this;
            this.message_is_follower = false;
            console.log('RECORDS:');
            console.log(records);
            this.followers = records || this.followers;
            // clean and display title
            var node_user_list = this.$('.oe_follower_list').empty();
            this.$('.oe_follower_title').html(this._format_followers(this.followers.length));
            self.message_is_follower = _.indexOf(this.followers.map(function (rec) { return rec[2]['is_uid']}), true) != -1;
            // truncate number of displayed followers
            var truncated = this.followers.slice(0, this.displayed_nb);
            _(truncated).each(function (record) {
                partner = {
                    'id': record[0],
                    'name': record[1],
                    'is_uid': record[2]['is_uid'],
                    'is_editable': record[2]['is_editable'],
                    'notify_email': record[2]['notify_email'],
                    'avatar_url': session.mail.ChatterUtils.get_image(self.session, 'res.partner', 'image_small', record[0])
                };
                console.log('partner');
                console.log(partner);
                $(session.web.qweb.render('mail.followers.partner', {'record': partner, 'widget': self})).appendTo(node_user_list);
                // On mouse-enter it will show the edit_subtype pencil.
                if (partner.is_editable) {
                    self.$('.oe_follower_list').on('mouseenter mouseleave', function(e) {
                        self.$('.oe_edit_subtype').toggleClass('oe_hidden', e.type == 'mouseleave');
                        self.$('.oe_follower_list').find('.oe_partner').toggleClass('oe_partner_name', e.type == 'mouseenter');
                    });
                }
            });
            // FVA note: be sure it is correctly translated
            if (truncated.length < this.followers.length) {
                $(session.web.qweb.render('mail.followers.show_more', {'number': (this.followers.length - truncated.length)} )).appendTo(node_user_list);
            }
        },
	
	    do_follow: function () {
	        /**
	         * Add this context value to force subscription
	         */	    	
	        var context = new session.web.CompoundContext(this.build_context(), {'force_subscription': 1});
            console.log('do_follow');

	        this.ds_model.call('message_subscribe_users', [[this.view.datarecord.id], [this.session.uid], undefined, context])
	            .then(this.proxy('read_value'));
	
	        _.each(this.$('.oe_subtype_list input'), function (record) {
	            $(record).attr('checked', 'checked');
	        });
	
	    }
    
    });

    // HINT: Add recipient_ids to MessageCommon - message common is extended by:
    //       mail.ThreadMessage AND
    //       mail.ThreadComposeMessage so both should have recipients_ids now for ThreadComposeMessage it will be
    //       useless for now because this is updated after we post the message.
    // session.mail.MessageCommon = session.mail.MessageCommon.extend({
    // HINT2: mail.MessageCommon did not work ?!?
    openerp.mail.ThreadMessage = openerp.mail.ThreadMessage.extend({
    	template: 'mail.thread.message',

    	init: function (parent, datasets, options) {
    		this._super(parent, datasets, options);

    		this.notified_by_email_ids = datasets.notified_by_email_ids || [];
    	}
    });

};
