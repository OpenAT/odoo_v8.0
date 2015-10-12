# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
from openerp.osv import orm

class website_as_widget(http.Controller):
    @http.route(['/aswidget'], type='http', auth="public", website=True)
    def page_as_widget(self, *args, **kwargs):
        # get aswiddget from kwargs or set it to True if not found: So one could call the URL with &aswidget=False to
        # reset the session and show header and footer again
        request.session['aswidget'] = kwargs.get('aswidget', True)
        widgeturl = kwargs.get('widgeturl', '/')
        # local_redirect found at addons/web/controllers/main.py line 467
        return http.local_redirect(widgeturl, query=request.params, keep_hash=True)


# found at addons/crm/ir_http.py
# Test the URL of every request (better would be to only test the urls of the correct sub controller of
# addons/web/controllers/main.py class Home but it works and has no performance impact ;) )
class ir_http(orm.AbstractModel):
    _inherit = 'ir.http'

    def _dispatch(self):
        response = super(ir_http, self)._dispatch()
        if 'aswidget' in request.httprequest.host:
            request.session['aswidget'] = True
        return response
