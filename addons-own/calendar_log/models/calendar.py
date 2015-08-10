# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp import tools


class calendar_event_category(osv.Model):
    _name = 'calendar.event.category'
    _description = 'Meeting Category'
    _columns = {
        'name': fields.char('Name', required=True, translate=True),
    }


class calendar_event(osv.Model):
    _inherit = ["calendar.event"]

    _columns = {
        'no_invitations': fields.boolean('No invitation e-mails!', help='Do not send invitation e-mails!'),
        'expense_allowance': fields.boolean('Expense Allowance', help='Eligible for expense refund!'),
        'odometer_start': fields.integer('Odometer at start'),
        'odometer_finish': fields.integer('Odometer at finish'),
        'category_id': fields.many2one('calendar.event.category', 'Category', required=True),
        'meeting_minutes': fields.text('Internal Meeting Minutes'),
    }
    _defaults = {
        'no_invitations': True,
    }


class calendar_attendee(osv.Model):
    _inherit = ["calendar.attendee"]

    # Filter out attendees for meetings where no_invitations is set to true
    def _send_mail_to_attendees(self, cr, uid, ids, email_from=tools.config.get('email_from', False),
                                template_xmlid='calendar_template_meeting_invitation', force=False, context=None):
        if context is None:
            context = {}
        new_ids = []
        for attendee in self.browse(cr, uid, ids, context=context):
            try:
                if not attendee.event_id.no_invitations:
                    new_ids += attendee.ids
            except:
                new_ids += attendee.ids
                pass

        return super(calendar_attendee, self)._send_mail_to_attendees(cr, uid, new_ids, email_from,
                                                                      template_xmlid, force, context)
