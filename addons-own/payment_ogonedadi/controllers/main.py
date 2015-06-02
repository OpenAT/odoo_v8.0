# -*- coding: utf-8 -*-
import logging
import pprint
import werkzeug

from openerp import http, SUPERUSER_ID
from openerp.http import request

_logger = logging.getLogger(__name__)


class OgonedadiController(http.Controller):
    _accept_url = '/payment/ogonedadi/test/accept'
    _decline_url = '/payment/ogonedadi/test/decline'
    _exception_url = '/payment/ogonedadi/test/exception'
    _cancel_url = '/payment/ogonedadi/test/cancel'

    @http.route([
        '/payment/ogonedadi/accept', '/payment/ogonedadi/test/accept',
        '/payment/ogonedadi/decline', '/payment/ogonedadi/test/decline',
        '/payment/ogonedadi/exception', '/payment/ogonedadi/test/exception',
        '/payment/ogonedadi/cancel', '/payment/ogonedadi/test/cancel',
    ], type='http', auth='none', website=True)
    def ogonedadi_form_feedback(self, **post):
        """ Ogone contacts using GET, at least for accept """
        _logger.info('Ogonedadi: entering form_feedback with post data: \n%s\n', pprint.pformat(post))  # debug
        cr, uid, context = request.cr, SUPERUSER_ID, request.context

        # Get the Tx related to the post data of ogone and store the current state of the tx
        tx_obj = request.registry['payment.transaction']
        tx = getattr(tx_obj, '_ogonedadi_form_get_tx_from_data')(cr, SUPERUSER_ID, post, context=context)
        state_old = False
        if tx:
            state_old = tx.state

        # Update the payment.transaction and the Sales Order:
        # form_feedback will call finally _ogonedadi_form_validate (call besides others) and return True or False
        # INFO: form_feedback is also inherited by website_sale and website_sale_payment_fix
        request.registry['payment.transaction'].form_feedback(cr, uid, post, 'ogonedadi', context=context)

        # If the state changed send an E-Mail (have to do it here since we do not call /payment/validate for ogonedadi)
        # HINT: we call a special E-Mail template "email_template_webshop" defined in website_sale_payment_fix
        #       for this to work we extended "action_quotation_send" interface with email_template_modell and ..._name
        if tx.state != state_old:
            _logger.info('Ogonedadi: Send E-Mail for Sales order: \n%s\n', pprint.pformat(tx.sale_order_id.name))
            email_act = request.registry['sale.order'].action_quotation_send(cr, SUPERUSER_ID,
                                                                             [tx.sale_order_id.id],
                                                                             context=context,
                                                                             email_template_modell='website_sale_payment_fix',
                                                                             email_template_name='email_template_webshop')
            if email_act and email_act.get('context'):
                composer_obj = request.registry['mail.compose.message']
                composer_values = {}
                email_ctx = email_act['context']
                template_values = [
                    email_ctx.get('default_template_id'),
                    email_ctx.get('default_composition_mode'),
                    email_ctx.get('default_model'),
                    email_ctx.get('default_res_id'),
                ]
                composer_values.update(composer_obj.onchange_template_id(cr, SUPERUSER_ID, None, *template_values, context=context).get('value', {}))
                if not composer_values.get('email_from') and uid == request.website.user_id.id:
                    composer_values['email_from'] = request.website.user_id.company_id.email
                for key in ['attachment_ids', 'partner_ids']:
                    if composer_values.get(key):
                        composer_values[key] = [(6, 0, composer_values[key])]
                composer_id = composer_obj.create(cr, SUPERUSER_ID, composer_values, context=email_ctx)
                composer_obj.send_mail(cr, SUPERUSER_ID, [composer_id], context=email_ctx)

        # Redirect ot our own Confirmation page (instead of calling /payment/validate)
        # all the stuff that could be done by /payment/validate for SO was already done by website_sale_payment_fix
        # "form_feedback" so we are no longer session variable dependent!
        if tx and tx.sale_order_id:
            #return request.website.render("website_sale_payment_fix.confirmation_static", {'order': tx.sale_order_id})
            return request.redirect('/shop/confirmation_static?order_id=%s' % tx.sale_order_id.id)

        # If no tx or tx.sale_order_id was found simply return to the root page of the website
        # return werkzeug.utils.redirect(post.pop('return_url', '/'))
        return werkzeug.utils.redirect('/')

    # ToDo by mike: add a new controller that will delete the payment.transaction and reset the sales order to draft
    #               so that the user can select an other payment provider - BUT only if he pressed just "back" on the
    #               ogone payment form without generating a payment - this should call a special URL (this controller)
    #               RULES: if this URL is called (with POST data to know the correct SO) and the related TX is still in
    #               state draft we will delete the tx and set the SO to state draft and set all relevant session
    #               variables if they are empty at current state. state 2 of ogone (user canceld payment) would also
    #               be valid!

    # Add a route for the ogone template
    @http.route(['/shop/ogonepayment', '/shop/ogonepayment.html'], type='http', auth="public", website=True)
    def ogonepayment(self, **post):
        cr, uid, context = request.cr, request.uid, request.context

        # get the current URL of the webpage to set the absolute links for the CSS Files in the template
        values = {
            "url": request.registry['ir.config_parameter'].get_param(cr, SUPERUSER_ID, 'web.base.url'),
            "dbname": cr.dbname
        }

        return request.website.render("payment_ogonedadi.ogonepayment", values)
