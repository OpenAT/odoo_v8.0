# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class calendar_event_category(osv.osv):
    _name = 'calendar.event.category'
    _description = 'Meeting Category'
    _columns = {
        'name': fields.char('Name', required=True, translate=True),
    }
