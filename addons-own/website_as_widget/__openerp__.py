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
    'name': "FCOM website_as_widget",
    'summary': """call webpages as widgets (without header or footer)""",
    'description': """

website_as_widget
=================

Call webpages as widgets (without header or footer).

**Call the page from a subdomain called aswidget:**

http://aswidget.ahch.datadialog.net/shop

**Call the page with aswidget=True and the page widgeturl=%2Fshop :**

http://ahch.datadialog.net/?aswidget=True&widgeturl=%2Fshop

**Show the page normally again (with header and footer):**

http://ahch.datadialog.net/?aswidget=False
This will remove the aswidget=True from the current session

**Session and Domains:**

It is always better to call the i-frame url from a sub-domain URL (ahch.datadialog.net) because this will generate a
different session for the subdomain and so one could still call the website with header and footer (different session)
from the other domain (ahch.datadialog.net)

**HINT:** Keep in mind that session cookies can be shared from parent domains to child (sub) domains but not the
other way around!

**Embed the Page as an iFrame**

https://github.com/davidjbradshaw/iframe-resizer
Please look at the example html file at website_as_widget/test_iframe.html

    """,
    'author': "Michael Karrer",
    'website': "http://www.datadialog.net/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'base', 'website', 'website_tools',
    ],
    'installable': True,
    'data': [
        'views/templates.xml',
    ],
}
