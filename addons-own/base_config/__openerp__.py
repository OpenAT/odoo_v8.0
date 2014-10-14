# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
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
    'name': "base_config",
    'summary': """Setup and Configuration Tool""",
    'description': """

base_config setup and configuration tool
========================================

This module makes it easy to setup and configure a new database for odoo. It ensures that all setups are basically
the same and makes it easy to include new default addons and settings.


Module tasks:
-------------
    - Install all common addons
    - Overwrite some of the backend CSS (forms-fullwidth, chatter, colors)
    - ToDo: Create a new configuration menu for addons-own and addons-thirdparty linked in addons-loaded
    - ToDo: Set default values for the admin user (timezone, technical features, language)
    - ToDo: Set/Create Project Stages
    - ToDo: Set/Create Issue/Opportunity Stages
    - ToDo: Load the Austrian set of Accounting Charts and set the right Taxes
    - ToDo: Setup Real-Time Warehouse Transactions, Create needed Accounts and use them in the product categories
    - ToDo: Set "Validate Timesheets every" to: Month
    - ToDo: Create a standard working schedules for 38,7 h and 40,0 h per week
    - ToDo: Set all other default values in "settings > configuration"

    """,
    'author': "OpenAT",
    'website': "http://www.openat.at/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'base', 'crm', 'mail',
        'account_voucher', 'project', 'note', 'project_issue', 'account_accountant', 'survey', 'sale','stock',
        'purchase', 'hr', 'hr_timesheet_sheet', 'hr_recruitment', 'hr_holidays', 'hr_expense', 'hr_evaluation',
        'calendar', 'contacts', 'gamification', 'im_livechat', 'lunch',
        'website', 'website_blog', 'website_event', 'website_forum', 'website_sale',
        'website_certification', 'website_crm', 'website_crm_partner_assign', 'website_customer', 'website_event_sale',
        'website_event_track', 'website_forum_doc', 'website_gengo', 'website_google_map', 'website_hr',
        'website_hr_recruitment', 'website_mail', 'website_mail_group', 'website_membership', 'website_partner',
        'website_payment', 'website_project', 'website_quote', 'website_report', 'website_sale',
        'website_sale_delivery', 'website_sale_options', 'website_twitter',
        'base_location', 'base_location_geonames_import', 'dbfilter_from_header', 'disable_openerp_online',
        'mass_editing', 'web_export_view',
    ],
    'installable': True,
    'css': [
        'static/src/css/chatter.css',
        'static/src/css/backend.css',
        'static/src/css/addons.css',
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
    'test': [
        #'tests/access_group_users.yml',
    ],
    'application': True,
    'auto_install': False,
    'images': [
        'static/src/img/icon.png',
    ],
}
