# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "website_sale_login",
    'summary': """FCOM better login pages and user detection by e-mail""",
    'description': """
website_sale_login
==================

Check e-mail address for existing partner or user account at checkout.

shop/checkout and shop/confirm_order

- User/Partner detection by e-mail in shop/checkout and shop/confirm_order controllers
- Show messages for signup or account creation if partner/user found
- Continue without signup and show messages only once or only at email change if web-user decides to go on without sign in / sign up
- Quick checkout possible through get variables transfers to /checkout with prefilled form and the product already in basket
  e.g.: /shop/simplecheckout/spenden-3?email=mike@test.com&name=Mike
- Anonymous quick checkout of products possible through simplecheckout urls with &directpayment=True parameter transfers to /payment with a new res.partner for the SO and the product already in basket
  e.g.: /shop/simplecheckout/spenden-3?email=mike2@test.com&shipping_id=0&country_id=13&directpayment=True

TODO:

- Checkbox for Account Creation
- Checkbox for Newsletter reception (Maybe an Extra addon or included in website_sale_donate)
- User Quick Checkout direct to payment (Security Risks have to be considered!) if parnter_id or User_id, email and name in post and all are valid (correct parnter_id or user_id for email and name) then use this partner/user and jump directly to the payment page /shop/simplecheckout/spenden-3?email=mike2@test.com&name=Michael_Karrer&shipping_id=0&country_id=13&partner_id=24


HINT:

This addon depends on auth_signup for signup or account creation and can be used with auth_doubleoptin also.

    """,
    'author': "Michael Karrer (michael.karrer@datadialog.net), DataDialog",
    'website': "http://www.datadialog.net/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'website_sale',
        'website_quote',
        'auth_signup',
    ],
    'installable': True,
    'data': [
        'views/templates.xml',
        #'email_template_data.xml',
    ]
}
