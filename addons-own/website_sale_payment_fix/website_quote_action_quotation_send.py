# -*- coding: utf-8 -*-
__author__ = 'Michael Karrer'

#from openerp import SUPERUSER_ID
from openerp import models

class sale_order(models.Model):
    _inherit = 'sale.order'

    # HINT: action_quotation_send is already overwritten by addon "website_quote" and "portal_sale"!
    def action_quotation_send(self, cr, uid, ids, context=None,
                              email_template_modell=None,
                              email_template_name=None):
        """ extend the interface of action_quotation_send to call it for a custom email template """
        action_dict = super(sale_order, self).action_quotation_send(cr, uid, ids, context=context)
        try:
            template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, email_template_modell, email_template_name)[1]
            if template_id:
                ctx = action_dict['context']
                ctx['default_template_id'] = template_id
                ctx['default_use_template'] = True
        except Exception:
            pass

        return action_dict
