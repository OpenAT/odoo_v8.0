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

{
    'name': 'auth_doubleoptin',
    'summary': """FCOM Double-Opt-In for account signup and newsletter subscription verification""",
    'description': """
FCOM Double-Opt-In System für User Account creation
===================================================

Double-Opt-In for account signup and newsletter subscription verification

- Add a new website controller /register to allow registration by e-mail or login after registration
- Send an e-mail with a "Set Password" link for user account verification
- Send an e-mail with validation link for newsletter subscription verification

## External Links
http://haacked.com/archive/2007/09/11/honeypot-captcha.aspx/
http://www.smashingmagazine.com/2011/05/innovative-techniques-to-simplify-signups-and-logins/
https://www.google.com/recaptcha/intro/index.html
https://developers.google.com/recaptcha/docs/start

    """,
    'author': 'Michael Karrer (michael.karrer@datadialog.net), DataDialog',
    'version': '1.0',
    'category': 'Authentication',
    'website': 'https://www.datadialog.net',
    'installable': True,
    'depends': [
        'auth_signup',
    ],
    'data': [
        'views/auth_doubleoptin.xml',
        #'auth_signup_data.xml',
    ],
    'bootstrap': True,
}
