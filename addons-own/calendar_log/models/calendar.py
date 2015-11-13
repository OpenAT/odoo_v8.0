# -*- coding: utf-8 -*-

from openerp import tools, api
from openerp.fields import Many2one, Boolean, Integer, Text
from openerp.osv import osv



class calendar_event(osv.osv):
    _inherit = 'calendar.event'
    # If we do not want to set a default value for category_id but still be able to install this addon in an existing
    # Database we could use the  _auto_init or even better the init method to execute an SQL query and prepopulate the
    # table - see addon website_sale_categories for an example
    # https://www.odoo.com/es_ES/forum/help-1/question/is-there-a-way-to-set-a-value-for-a-field-for-all-existing-records-in-the-database-at-addon-installation-only-89400
    # https://gist.github.com/lepistone/3ca65107fc7344440777

    @api.model
    def _get_category(self):
        category = self.env.ref("calendar_category.category_generalactivity", raise_if_not_found=False)
        if not category:
            category = self.env['calendar.event.category'].search([], limit=1, order='id')
        return category

    no_invitations = Boolean(string='No invitation e-mails!', help='Do not send invitation e-mails!', default=True)
    odometer_start = Integer(string='Odometer at start')
    odometer_finish = Integer(string='Odometer at finish')
    category_id = Many2one('calendar.event.category', string='Category', required=True,
                           default=lambda self: self._get_category())
    meeting_minutes = Text('Internal Meeting Minutes')
    mainpartner_id = Many2one('res.partner', string='Main Partner')

    @api.onchange('mainpartner_id')
    def _add_attendee(self):
        if self.mainpartner_id:
            # http://odoo-new-api-guide-line.readthedocs.org/en/latest/environment.html#the-ids-attribute
            # http://www.mindissoftware.com/2014/11/07/Understand-Odoo-Model-Part1
            # https://github.com/odoo/odoo/issues/2693
            # https://www.odoo.com/fr_FR/forum/help-1/question/how-to-add-records-in-many2many-field-82878
            # https://www.odoo.com/fr_FR/forum/help-1/question/how-to-insert-value-to-a-one2many-field-in-table-with-create-method-28714
            # https://www.odoo.com/fr_FR/forum/help-1/question/insert-new-record-into-one2many-field-20931
            self.partner_ids = [(4, self.mainpartner_id.id)]


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
