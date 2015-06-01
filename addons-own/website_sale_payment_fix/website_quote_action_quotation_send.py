# -*- coding: utf-8 -*-
__author__ = 'Michael Karrer'

#from openerp import SUPERUSER_ID
from openerp import models

class sale_order(models.Model):
    _inherit = 'sale.order'

    # HINT: action_quotation_send is already overwritten by addon website_quote so we need to depend on this addon
    #       to be sure we get inherited after website_quote
    def action_quotation_send(self, cr, uid, ids, context=None,
                              email_template_modell='website_quote',
                              email_template_name='email_template_edi_sale'):
        action = super(sale_order, self).action_quotation_send(cr, uid, ids, context=context)
        ir_model_data = self.pool.get('ir.model.data')
        quote_template_id = self.read(cr, uid, ids, ['template_id'], context=context)[0]['template_id']
        if quote_template_id:
            try:
                template_id = ir_model_data.get_object_reference(cr, uid, email_template_modell, email_template_name)[1]
            except ValueError:
                pass
            else:
                action['context'].update({
                    'default_template_id': template_id,
                    'default_use_template': True
                })

        return action
