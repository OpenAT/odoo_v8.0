# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
import logging
import werkzeug

import openerp
from openerp import SUPERUSER_ID
from openerp.addons.auth_signup.res_users import SignupError
from openerp.addons.web.controllers.main import ensure_db
from openerp import http
from openerp.http import request
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class AuthDoubleOptIn(openerp.addons.auth_signup.controllers.main.AuthSignupHome):

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

    def signup_by_email(self, email, qcontext=None, token=False):
        if not qcontext:
            qcontext = {}
        users_obj = request.registry.get('res.users')
        message = str()
        error = str()

        try:
            # Create new user with new partner or use existing partner if token given
            # INFO: "signup" will create a new user (and related partner) with "_signup_create_user" but
            #       "_signup_create_user" sets "no_reset_password=True" so no email is send to the user
            #       because of this we have to run "reset_password" after signup
            if qcontext or token:
                qcontext['login'] = qcontext.get('login', email)
                users_obj.signup(request.cr, SUPERUSER_ID, qcontext, token)
                message += _("Your account was created!<br/>")

            # Send the user a password reset email (Double Opt In)
            # INFO: only works if user.login = user.email (as expected but not forced by odoo)
            users_obj.reset_password(request.cr, SUPERUSER_ID, email)
            message += _("To verify your account an email has been send to you!<br/>"
                         "Please use the link in the e-mail to set your password!<br/><br/>"
                         "After you set your password please continue by clicking the login button below.")

            # Update the qcontext with the message
            qcontext['message'] = qcontext.get('message', str()) + message
        except (SignupError, AssertionError, Exception), e:
            # remove success message
            if qcontext.get('message'):
                del qcontext['message']

            # update qweb error message
            error += _("Could not create your account!\n")

            # Extend error message for the website
            if hasattr(e, 'name'):
                error += '<br/>' + _(e.name)
            if hasattr(e, 'message'):
                error += '<br/>' + _(e.message)
            qcontext['error'] = error

            # Extend error message for the log
            if hasattr(e, 'value'):
                error += _(e.value)
            _logger.exception(error)
            pass

        return qcontext

    @http.route(['/web/register',
                 '/register'],
                type='http', auth='public', website=True)
    def web_auth_register(self, *args, **post):
        cr, uid, context = request.cr, request.uid, request.context

        if 'button_login' in post:
            # INFO: html escaping is done by request.redirect so not needed here!
            query = '&'.join("%s=%s" % (key, val) for (key, val) in post.iteritems() if val)
            return request.redirect('/web/login?' + query)

        # INFO: Adds the auth_signup_config to qcontext
        #       Adds the partner fields to qcontext if a token is already in **post
        #       if no token it will simply return the request.params
        qcontext = self.get_auth_signup_qcontext()
        email = qcontext.get('email') or qcontext.get('login')

        if email and 'error' not in qcontext:
            #ToDo: Limit password and user create requests to max 5/hour/session and 10/hour/ip
            #      Store register_request_first register_request_last register_request_count
            partner_obj = request.registry.get('res.partner')

            # User found: Send password reset email
            if self.userid_by_email(email):
                # INFO: Do not transfer qcontext to signup_by_mail
                #       since we only want to send password reset email in this case:
                qcontext.update(self.signup_by_email(email))

            # One Partner found: Create Token, Create User, Send password-reset-email
            elif self.partnerid_by_email(email) and len(self.partnerid_by_email(email)) == 1:

                partner = partner_obj.browse(cr, SUPERUSER_ID, self.partnerid_by_email(email)[0], context)
                if not partner.user_ids:
                    # Generate a new token for the res.partner
                    partner_obj.signup_prepare(cr, SUPERUSER_ID, partner.id, context)
                    qcontext.update({'token': partner.signup_token})
                    qcontext = self.signup_by_email(email, qcontext, partner.signup_token)

            # Name and email in qcontext: Create new partner and user, Send password-reset-email
            elif email and qcontext.get('name'):
                qcontext = self.signup_by_email(email, qcontext)

            # email was found but no user found no partner found and no name in post = error
            else:
                qcontext['error'] = _("Wrong e-mail address or name missing!")

        return request.render('auth_doubleoptin.register', qcontext)

    # DISABLE /web/signup -> redirect to /web/register:
    @http.route()
    def web_auth_signup(self, *args, **kw):
        return request.redirect('/web/register' + '?' + request.httprequest.query_string)

