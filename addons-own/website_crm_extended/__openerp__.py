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
    'name': "website_crm_extended",
    'summary': """Send E-Mail to company mail address for contact form of website""",
    'description': """

website_crm_sendmail
====================

A very simple addon to post an additional Chatter notification with better information on lead creation
if someone uses the oddo cms contact form. Also it sets the sales team for the new lead to website sales so you could
configure the follwoers and therefore the external mails send.

This is also the place to add additional extensions to the website.crm addon (the website contact form of odoo):

- Added: Add res.partner to lead if E-Mail or name matches

    """,
    'author': "OpenAT",
    'website': "http://www.openat.at/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'base', 'website_crm',
    ],
    'installable': True,
}