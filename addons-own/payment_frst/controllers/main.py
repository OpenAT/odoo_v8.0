# -*- coding: utf-8 -*-
import logging
import pprint
import werkzeug

from openerp import http, SUPERUSER_ID
from openerp.http import request

_logger = logging.getLogger(__name__)


class FRSTController(http.Controller):
    _accept_url = '/payment/frst/feedback'

    # This route is called through the "pay now" button on the /shop/payment page
    @http.route(['/payment/frst/feedback'], type='http', auth='none')
    def frst_form_feedback(self, **post):
        cr = request.cr
        uid = SUPERUSER_ID
        context = request.context

        _logger.info('Beginn Form Feedback for FRST PaymentProvider with post data %s', pprint.pformat(post))

        # HINT: At this point a sales.order AND a payment.transaction already exist
        #       They are created or updated through website.sale_get_order
        #       in "addons/website_sale/models/sale_order.py" in "class class website(orm.Model):"
        #
        #       The res.partner was already created through "self.checkout_form_save(values["checkout"])"
        #       in "addons/website_sale/controllers/main.py" at "@http.route(['/shop/confirm_order']..."
        #
        # The method "form_feedback" will:
        #
        # 1.) call "_frst_form_get_tx_from_data"
        #     to get the id for the transaction linked to the current sales order
        #
        # 2.) call "_frst_form_get_invalid_parameters"
        #     to check for any invalid parameters (here we check iban and bic) if any invalid parameters are found
        #     it will stop and return False
        #
        # 3.) call "_frst_form_validate"
        #     returns true if the payment povider sended a correct state like "PENDING" or "AUTHORIZED" -> This is
        #     dependend on the payment provider or it will return FALSE if the answer was not understandable. But in
        #     our case we do not talk to an PP so we simply return "tx.write({'state': 'pending'})" which also gives
        #     back true or false depending if it worked or not ;)
        #     HINT: !! We do also update the BankAccount with the IBAN and BIC for the partner in this method !!
        #
        # ToDo:     What i really do not understand is what happens if form_feedback gets false returned? Right
        # ToDo:     now nothing really happens but that "_frst_form_validate" is not reached!?!
        #
        #
        # Todo: If we want the Iban and BIC to be pre filled if available in the Aquirer button form we would have to
        # Todo: use tx_values of the "render" method in addons/payment/models/payment_acquirer.py because this method
        # Todo: do not have an generic interface like **kwargs. This "render" method is used in
        # Todo: addons/website_sale/controllers/main.py "acquirer.button = payment_obj.render" we would need to update
        # Todo: this tx_values there before the template website_sale.payment (addons/website_sale/views/templates.xml)
        # Todo: is rendered.
        #
        # Todo: Payment transaction should not be sucessfull if "_frst_form_validate" did not run because of
        # Todo: "_frst_form_get_invalid_parameters" had error fields and returned to early

        request.registry['payment.transaction'].form_feedback(cr, uid, post, 'frst', context)



        return werkzeug.utils.redirect(post.pop('return_url', '/'))
