# -*- coding: utf-'8' "-*-"
__author__ = 'mkarrer'

import base64
try:
    import simplejson as json
except ImportError:
    import json
import logging
import urlparse
import werkzeug.urls
import urllib2
import pprint

from openerp.addons.payment.models.payment_acquirer import ValidationError

# Import the FRST Controller - this is only possilbebecause we add payment_frst to the main class later in this file
from openerp.addons.payment_frst.controllers.main import FRSTController
from openerp.osv import osv, fields
from openerp.tools.float_utils import float_compare
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)


# This class modifies the payment.acquirer class: this will add new payment providers to odoo. Payment Providers Objects
# hold all the relevant data to talk with an payment provider like urls, secrets and data (tx_values)
#
# Since we do not talk to any external payment provider we do not need most of the methods and variables seen in the
# paypal or adyen pp.
class AcquirerFRST(osv.Model):
    _inherit = 'payment.acquirer'

    # Add a new Acquirer
    def _get_providers(self, cr, uid, context=None):
        providers = super(AcquirerFRST, self)._get_providers(cr, uid, context=context)
        providers.append(['frst', 'FRST'])
        return providers

    # Add Additional tx values for the aquirer button form
    # There is a hook inside the .render method in "addons/payment/models/payment_acquirer.py"
    # The .render method is called by "addons/website_sale/controllers/main.py" at route /shop/payment to render
    # the aquirer buttons. at this point partner_id and sales_order is normally known
    #
    # Hint: This .render method uses the original .render method of ir.ui.view in the end to render a qweb template
    #
    # The aquirer button rendering itself is triggered at addons/website_sale/controllers/main.py
    # line 659: "acquirer.button = payment_obj.render" at route /shop/payment
    #
    # Transaction values ar given to ".render". Inside render the above mentioned hook adds acquirer specific values to
    # partner_values and tx_values (which are pre-processed at "form_preprocess_values directly in render") and then
    # used in the dictionary qweb_context wich is used to render the qweb template for the acquirer button form
    def frst_form_generate_values(self, cr, uid, id, partner_values, tx_values, context=None):
        frst_partner_values = dict(partner_values)
        frst_partner_values.update({
                'frst_iban': '',
                'frst_bic': '',
            })
        partner = tx_values.get('partner')
        if partner.bank_ids:
            frst_partner_values.update({
                'frst_iban': partner.bank_ids[-1].acc_number or '',
                'frst_bic': partner.bank_ids[-1].bank_bic or '',
            })
        return frst_partner_values, tx_values



    # Define the Form URL (url that will be called when button with form is clicked)
    def frst_get_form_action_url(self, cr, uid, id, context=None):
        return '/payment/frst/feedback'




# This class creates the payment transaction objects. So the objects that are created through an checkout (payment)
# process
class PaymentTransactionFRST(osv.Model):
    _inherit = 'payment.transaction'

    _columns = {
        'frst_iban': fields.char('IBAN'),
        'frst_bic': fields.char('BIC'),
    }

    # Get all related stored Transactions for the current Reference Number
    def _frst_form_get_tx_from_data(self, cr, uid, data, context=None):

        # the current sales order is stored in reference
        reference = data.get('reference')

        # search for transactions linked to this sales order
        tx_ids = self.search(cr, uid, [('reference', '=', reference),], context=context)
        if not tx_ids or len(tx_ids) > 1:
            error_msg = 'FRST Payment Transaction: received data for reference %s' % (pprint.pformat(reference))
            if not tx_ids:
                error_msg += '; no Transaction found'
            else:
                error_msg += '; multiple Transactions found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        # return the payment.transaction object
        return self.browse(cr, uid, tx_ids[0], context=context)

    # Check the Received (tx) values against local (data) ones: Amount and the Currency
    # (This is not really needed since we are our own payment provider but for demonstration it is used here)
    def _frst_form_get_invalid_parameters(self, cr, uid, tx, data, context=None):
        invalid_parameters = []

        # Compare the local amount with the amount from the PP
        if float_compare(float(data.get('amount', '0.0')), tx.amount, 2) != 0:
            invalid_parameters.append(('amount', data.get('amount'), '%.2f' % tx.amount))

        # Compare the local currency with the currency of the pp
        if data.get('currency') != tx.currency_id.name:
            invalid_parameters.append(('currency', data.get('currency'), tx.currency_id.name))

        # Check IBAN
        if not data.get('frst_iban'):
            invalid_parameters.append(('frst_iban', data.get('frst_iban'), 'At least some value '))

        # Check BIC
        if not data.get('frst_bic'):
            invalid_parameters.append(('frst_bic', data.get('frst_bic'), 'At least some Value'))

        info_msg = 'FRST Payment Transaction: Invalid Parameters %s' % (pprint.pformat(invalid_parameters))
        _logger.info(info_msg)
        print '----'
        print info_msg
        print '----'

        return invalid_parameters

    # do the form validation and directly set the state of the payment.transaction to pending
    def _frst_form_validate(self, cr, uid, tx, data, context=None):
        _logger.info('Validated frst payment for tx %s: set as pending' % (tx.reference))

        # Create Bank Account with IBAN and BIC (res.partner.bank) for current res_partner
        iban = data.get('frst_iban')
        bic = data.get('frst_bic')
        partner = tx['partner_id']
        partner_id = partner.id
        bank_accounts = self.pool['res.partner.bank']
        accounts = bank_accounts.search(cr, uid,
                                        [('partner_id', '=', partner_id), ('acc_number', '=', iban)])
        if not accounts:
            bank_accounts.create(cr, SUPERUSER_ID,
                                 {'state': 'iban',
                                  'partner_id': partner_id,
                                  'acc_number': iban,
                                  'bank_bic': bic, },
                                 context=context)

        # Update State, Iban And BIC
        return tx.write({'state': 'pending', 'frst_iban': iban, 'frst_bic': bic, })