# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 OpenERP s.a. (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "website_crm_sendmail",
    'summary': """Send E-Mail to company mail address for contact form of website""",
    'description': """

website_crm_sendmail
====================

A very simple addon to send an E-Mail to the company E-Mail address.

    """,
    'author': "OpenAT",
    'website': "http://www.openat.at/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'base', 'website_crm',
    ],
    'installable': True,
    'css': [
        #'static/src/css/chatter.css',
        #'static/src/css/backend.css',
        ],
    'data': [
        # DATA
        #'data/data.xml',
        # SECURITY FILES
        #'security/ir.model.access.csv',
        #'security/ir_ui_view.xml',
        # VIEWS AND TEMPLATES
        #'views/res_config.xml',
        #'views/ir_actions.xml',
        #'views/templates.xml',
        #'views/snippets.xml',
        #'views/views.xml',
    ],
    'js': [
        #'static/src/js/default.js',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'data/demo.xml',
    ],
}