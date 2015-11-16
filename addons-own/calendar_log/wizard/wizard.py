# -*- coding: utf-8 -*-

from openerp import models, api
from openerp.fields import Many2one

class ReplaceCategoryWizard(models.TransientModel):
    _name = 'calendar_log.replace_eventcategory_wizard'

    category_old_id = Many2one('calendar.event.category', string='Old Category')
    category_new_id = Many2one('calendar.event.category', string='Replaced by Category')

    @api.multi
    def replace_category(self):

        # Replace the old category in every calendar.event with the new one
        events = self.env['calendar.event'].search([('category_id', '=', self.category_old_id.id)])

        # Debug
        print "EVENTS: %s" % events.ids
        for event in events:
            print "Event Name: %s  Old Kategory: %s" % (event.name, event.category_id.name)

        events.write({'category_id': self.category_new_id.id})

        # Debug
        for event in events:
            print "Event Name: %s  New Kategory: %s" % (event.name, event.category_id.name)
            #event.category_id = self.category_new_id

        # Do not store any reference to the Categories or they can not be deleted (seems like a odoo bug to mee):
        oldcatid = self.category_old_id.id
        self.category_old_id = False
        self.category_new_id = False

        # Remove the old category
        self.env['calendar.event.category'].browse(oldcatid).unlink()
        return {}
