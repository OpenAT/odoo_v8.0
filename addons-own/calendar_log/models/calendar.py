# -*- coding: utf-8 -*-

from openerp import tools, api
from openerp.fields import Many2one, Boolean, Integer, Text
from openerp.osv import fields, osv


class calendar_event(osv.osv):
    _inherit = 'calendar.event'

    @api.model
    def _get_category(self):
        category = self.env.ref("calendar_category.category_internalmeeting", raise_if_not_found=False)
        if not category:
            category = self.env['calendar.event.category'].search([], limit=1, order='id')
        return category

    no_invitations = Boolean(string='No invitation e-mails!', help='Do not send invitation e-mails!', default=True)
    expense_allowance = Boolean(string='Expense Allowance', help='Eligible for expense refund!')
    odometer_start = Integer(string='Odometer at start')
    odometer_finish = Integer(string='Odometer at finish')
    category_id = Many2one('calendar.event.category', string='Category', required=True,
                           default=lambda self: self._get_category())
    meeting_minutes = Text('Internal Meeting Minutes')


class calendar_event_category(osv.osv):
    _name = 'calendar.event.category'
    _description = 'Meeting Category'
    _columns = {
        'name': fields.char('Name', required=True, translate=True),
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
