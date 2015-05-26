# -*- coding: utf-8 -*-
__author__ = 'Michael Karrer'

from openerp import SUPERUSER_ID
from openerp.osv import orm, fields

class PaymentTransaction(orm.Model):
    _inherit = 'payment.transaction'

    def form_feedback(self, cr, uid, data, acquirer_name, context=None):
        """ Override to confirm the sale order, if defined, and if the transaction
        is done. """
        tx = None

        # RES could be True, False or, just if implemented by the PP, the Transaction ID
        res = super(PaymentTransaction, self).form_feedback(cr, uid, data, acquirer_name, context=context)

        # Fetch the tx, check its state, confirm the potential SO
        # (we have to do it this way since it is not sure that any PP returns the TX ID for _%s_form_validate but
        #  the output of this method will normally be returned by form_feedback therefore we have to call
        #  _%s_form_get_tx_from_data again to make sure to find the TX if any)
        tx_find_method_name = '_%s_form_get_tx_from_data' % acquirer_name
        if hasattr(self, tx_find_method_name):
            tx = getattr(self, tx_find_method_name)(cr, uid, data, context=context)

        # Payment Transaction States
        # --------------------------
        if tx and tx.sale_order_id:
            # DONE state is already done in website_sale_payment but it does not harm to have it here again
            # Normally at this point the SO should already be in a confirmed state (done when payment button is pressed)
            if tx.state in ['pending', 'done'] and tx.sale_order_id.state in ['draft', 'sent']:
                self.pool['sale.order'].action_button_confirm(cr, SUPERUSER_ID, [tx.sale_order_id.id], context=context)
            if tx.state in ['cancel', 'error'] and tx.sale_order_id.state != 'cancel':
                self.pool['sale.order'].action_cancel(cr, SUPERUSER_ID, [tx.sale_order_id.id], context=context)

        return res
