# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 OpenERP s.a. (<http://openerp.com>).
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
    'name': "website_sale_payment_fix",
    'summary': """Fix odoo Shop Payment Process""",
    'description': """

website_sale_payment_fix
========================

This addon fixes the session depended payment process of odoo 8.0 website_sale shop in combination with the
payment_ogone_dadi payment provider which is a replacement of the odoo ogone payment provider.

The problem of the original odoo payment process is that the update of the payment transaction and the related sales
order is dependent on the data of the current request.session. But it might be that the answer from ogone is received
later and not related to the current session at all and also send by ogone multible times for the same or different
states of the particullar payment.transaction.

To solve this we did:
- **clear the session variables** sale_order_id, sale_last_order_id, sale_transaction_id, sale_order_code_pricelist_id
  so a new Sales Order would be generated if the user opens the shop again.
  AND **set the sales order to state bestätigt** so that no changes are possible
  after the button of the PP in shop/payment is pressed (JSON calls method payment_transaction in website_sale main.py)

- If we receive an answer from the PP **all the logic for the Sales Order is done at method form_feedback** (website_sale
  did this already partially for setting the SO to state done but did not react to all possible states) so we do no
  longer depend on /shop/payment/validate to set the other states for the SO. This was needed because payment_validate
  did use session variables to find the payment.transaction and the sales.order but since the answer of the PP can be
  defered this is not always correct.

- All the other stuff is done in the addon payment_ogone_dadi - read its description too!

    """,
    'author': "Michael Karrer (michael.karrer@datadialog.net), DataDialog",
    'website': "http://www.datadialog.net/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'website_sale',
        'website_quote',
    ],
    'installable': True,
    'data': [
        'templates.xml',
        'email_template_data.xml',
    ]
}
