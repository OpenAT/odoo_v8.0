openerp.chatterimprovements = function (openerp) {
	
	openerp.mail_followers.Followers = openerp.mail_followers.Followers.extend({
    	
    	/**
    	 * Add field "notification_email_send" to follower records
    	 */
        fetch_followers: function (value_) {
            this.value = value_ || {};
            return this.ds_follow.call('read', [this.value, ['name', 'user_ids','notification_email_send']])
                .then(this.proxy('display_followers'), this.proxy('fetch_generic'))
                .then(this.proxy('display_buttons'))
                .then(this.proxy('fetch_subtypes'));
        },
	
	    do_follow: function () {
	        /**
	         * Add this context value to force subscription
	         */	    	
	        var context = new openerp.web.CompoundContext(this.build_context(), {'force_subscription': 1});

	        this.ds_model.call('message_subscribe_users', [[this.view.datarecord.id], [this.session.uid], undefined, context])
	            .then(this.proxy('read_value'));
	
	        _.each(this.$('.oe_subtype_list input'), function (record) {
	            $(record).attr('checked', 'checked');
	        });
	
	    }, 
    
    });
	
    openerp.mail.ThreadMessage = openerp.mail.ThreadMessage.extend({
    	template: 'mail.thread.message',
    		
    	init: function (parent, datasets, options) {
    		this._super(parent, datasets, options);
    		this.notified_email_ids = datasets.notified_email_ids ||  [];
    	}
    });

};
