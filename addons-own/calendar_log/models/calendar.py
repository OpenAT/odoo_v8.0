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
        'category_id': fields.many2one('calendar.event.category', 'Category', required=True),
    }
    _defaults = {
        'no_invitations': True,
    }


class calendar_attendee(osv.Model):
    _inherit = ["calendar.attendee"]

    def _send_mail_to_attendees(self, cr, uid, ids, email_from=tools.config.get('email_from', False),
                                template_xmlid='calendar_template_meeting_invitation', force=False, context=None):
        if context is None:
            context = {}
        new_ids = []
        for attendee in self.browse(cr, uid, ids, context=context):
            if not attendee.event_id.no_invitations:
                new_ids += attendee.ids

        return super(calendar_attendee, self)._send_mail_to_attendees(cr, uid, new_ids, email_from,
                                                                      template_xmlid, force, context)
