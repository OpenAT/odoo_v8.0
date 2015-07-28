# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale

class website_sale_login(website_sale):
    # Return True if there is an res.user with the email given
    def userid_by_email(self, email=None):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        user_obj = registry.get('res.users')
        userid = user_obj.search(cr, SUPERUSER_ID, [("email", "=", email)], context=context)
        # Return list of found users
        userid = userid if len(userid) >= 1 else None
        return userid

    def partnerid_by_email(self, email=None):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        partner_obj = registry.get('res.partner')
        partnerid = partner_obj.search(cr, SUPERUSER_ID, [("email", "=", email)], context=context)
        # Return the list of found Partners or None
        partnerid = partnerid if len(partnerid) >= 1 else None
        return partnerid

    # Not used right now but kept for reference:
    def order_has_partner(self):
        # Check if the SO has a different partner than the public-partner (partner of the public website user)
        order = request.website.sale_get_order(context=context)
        if order and order.partner_id:
            domain = [("partner_id", "=", order.partner_id.id)]
            user_ids = request.registry['res.users'].search(cr, SUPERUSER_ID, domain, context=dict(context or {}, active_test=False))
            # If NO user was found for the SO partner or if the user(s) found is NOT the public website user
            # than we know that the partner of the SO is a (new) private partner - akward i know :)
            if not user_ids or request.website.user_id.id not in user_ids:
                return order.partner_id
        return False

    def check_user(self, values):
        session = request.session
        postdict = request.httprequest.values or {}

        # Make sure the request-user is NOT logged in
        # Or skip user and partner checks if directpayment is set in the post variables:
        #     This makes it possible to create anonymous direct checkout links like:
        #     /shop/simplecheckout/spenden-3?email=mike2@test.com&name=Mike&shipping_id=0&country_id=13&directpayment=True
        if request.uid == request.website.user_id.id and not postdict.get('directpayment'):
            # Assert checkout dict is in values
            try:
                assert values.get('checkout')
            except:
                return values

            # Get email and name from values['checkout'] or post data
            email = values['checkout'].get('email') or postdict.get('email') or None
            name = values['checkout'].get('name') or postdict.get('name') or None

            # Update the checkout dict with name and email for qweb template rendering
            values['checkout'].update({'email': email, 'name': name})

            if email:

                # Check if the Email has changed
                if session.get('email_checkout') != email:

                    # Search for a users or partners with this email
                    partnerid_by_email = False
                    userid_by_email = self.userid_by_email(email)
                    if not userid_by_email:
                        partnerid_by_email = self.partnerid_by_email(email)

                    # If a user or partner was found extend checkout
                    if userid_by_email or partnerid_by_email:
                        values['checkout'].update(
                            {'userid_by_email': userid_by_email,
                             'partnerid_by_email': partnerid_by_email
                             })

            # Store the Email in the session to detect changes in subsequent calls of /checkout or /confirm_order
            session.update({'email_checkout': email})

        return values

    def checkout_values(self, data=None):
        values = super(website_sale_login, self).checkout_values(data)
        values = self.check_user(values)
        return values

    def checkout_form_validate(self, data):
        error = super(website_sale_login, self).checkout_form_validate(data)
        if data.get('userid_by_email') or data.get('partnerid_by_email'):
            error.update({'email_changed': True})
        return error

    # @http.route()
    # def checkout(self, **post):
    #     return self.check_user(super(website_sale_login, self).checkout(**post), **post)

    # @http.route()
    # def confirm_order(self, **post):
    #     return self.check_user(super(website_sale_login, self).confirm_order(**post), **post)


