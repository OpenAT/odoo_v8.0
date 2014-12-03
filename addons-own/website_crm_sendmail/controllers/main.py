# -*- coding: utf-8 -*-

# since this is no standard model.Model class but a http.Controller class the inheritance mechanisms of odoo would not
# work so we have to use classic python inheritance
#import openerp.addons.website_crm.controllers.main as main

from openerp import http, SUPERUSER_ID
from openerp.http import request
#from openerp.tools.translate import _

import openerp.addons.website_crm.controllers.main as main

class contactus_extended(main.contactus):

    def create_lead(self, request, values, kwargs):

        # Create a new Lead (request.registry is deprocated - should use request.env instead)
        values['section_id'] = request.env.ref('website.salesteam_website_sales').id
        newlead = request.registry['crm.lead'].create(request.cr, SUPERUSER_ID, values, request.context)

        # Get a Recordset from crm.lead - in this case a singleton
        leadrecord = request.env['crm.lead'].browse(newlead)
        #leadrecord.section_id = request.env.ref('website.salesteam_website_sales').id
        #leadrecord.write({'section_id': request.env.ref('website.salesteam_website_sales').id})

        # Search if a res.partner with the same E-Mail or if not with an similar name exists and add this to the
        # lead if more then one are asign not partner (then we have to do it manually)
        partners = request.env['res.partner'].search([('email', '=', values['email_from'])])
        if len(partners.ids) == 1:
            leadrecord.partner_id = partners.id

        if len(partners.ids) == 0:
            partners = request.env['res.partner'].search([('name', 'ilike', values['contact_name'])])
            if len(partners.ids) == 1:
                leadrecord.partner_id = partners.id

        # Post a New Message to this record
        # Todo use a Mail-Template (so translation would be working too!)
        recordtext = 'Neue Webanfrage: \n\nVon: %s\nE-Mail: %s\nPhone: %s\nFirma: %s\n\nBetreff: %s\nNachricht: %s' % (
            values['contact_name'],
            values['email_from'],
            values['phone'],
            values['partner_name'],
            values['name'],
            values['description'],
        )
        leadrecord.message_post(body=recordtext, subject=values['name'], type='notification', subtype='mail.mt_comment', content_subtype='plaintext')
        #leadrecord.message_post(body=recordtext, subject=values['name'])

        return newlead