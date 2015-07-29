# -*- coding: utf-8 -*-
__author__ = 'mkarrer'


import logging
from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
import numbers

# import the base controller class to inherit from
from openerp.addons.website_sale.controllers.main import website_sale

class website_sale_payment_fix(website_sale):
    # Overwrite the Json controller for the pay now button
    @http.route()
    def payment_transaction(self, acquirer_id):
        """ Method is called by JSON if the pay now button at the payment page is pressed. The user will be redirected
        to the Payment Provider. Until we get an answer from the PP we have no idea what the real state of this process
        is so we lock the SO and reset the current shop session variables.

        :param acquirer_id:
        :return:
        """
        cr, uid, context = request.cr, request.uid, request.context

        # Call the original method
        tx_id = super(website_sale_payment_fix, self).payment_transaction(acquirer_id)

        # Check if we received a real id (could also return a redirect)
        if tx_id and isinstance(tx_id, numbers.Number):
            # get the payment.transaction
            tx = request.registry['payment.transaction'].browse(cr, SUPERUSER_ID,
                                                                [tx_id], context=context)

            # Only reset the current shop session for our own providers
            if tx.acquirer_id.provider in ('ogonedadi', 'frst'):
                # Confirm the sales order so no changes are allowed any more
                request.registry['sale.order'].action_button_confirm(cr, SUPERUSER_ID,
                                                                     [tx.sale_order_id.id], context=context)
                # Clear the session to restart SO in case we get no answer from the PP or the user klicks back
                request.session.update({
                    'sale_order_id': False,
                    'sale_last_order_id': False,
                    'sale_transaction_id': False,
                    'sale_order_code_pricelist_id': False,
                })

        return tx_id

    # Add a Route for the alternative confirmation page
    @http.route(['/shop/confirmation_static'], type='http', auth="public", website=True)
    def payment_confirmation_static(self, order_id=None, **post):
        cr, uid, context = request.cr, request.uid, request.context
        try:
            order_id = int(order_id)
            order = request.registry['sale.order'].browse(cr, SUPERUSER_ID, order_id, context=context)[0]
            if order and order.name and order.payment_tx_id:
                return request.website.render("website_sale_payment_fix.confirmation_static", {'order': order})
            else:
                raise
        except:
            return request.website.render("website_sale_payment_fix.confirmation_static", {'order': None})
