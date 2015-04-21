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
    'name': "website_highlight_code",
    'summary': """One line to describe the addon""",
    'description': """

website_highlight_code
======================

This addon integrates code highlighting to the odoo web CMS.
Right now this only works for posts in website_forum!

In future version there will be also options to include this in normal edit mode for webpages and not just in the Forum.
(for this we would have to add a button to the inline CKEDITOR and make sure PRISM is not loaded in edit mode!)


Optional Ideas (not done yet):
------------------------------
- Extend plugin pbckode to use external files like GIST with PRISM code highlighter (extra field)
- Include pbckode also in normal edit mode (CKEDITOR inline mode for webcms)

Info:
-----
http://stackoverflow.com/questions/12531002/change-ckeditor-toolbar-dynamically
http://cdn.ckeditor.com/
http://docs.ckeditor.com/
http://docs.ckeditor.com/#!/api/CKEDITOR.plugins-method-addExternal
http://pierrebaron.fr/pbckcode/docs/
https://highlightjs.org/download/
http://stackoverflow.com/questions/20900041/how-to-remove-event-listeners-while-destroying-ckeditor
http://docs.ckeditor.com/#!/guide/dev_jquery
http://stackoverflow.com/questions/1794219/ckeditor-instance-already-exists

http://ace.c9.io/#nav=about
https://github.com/ajaxorg/ace-builds
http://www.jsdelivr.com/#!ace
http://cdnjs.com/libraries/ace/

// Remove PRISM changes for already processes nodes e.g.: when switching to edit mod in web cms
document.getElementsByTagName("CODE")[0].textContent = document.getElementsByTagName("CODE")[0].textContent;

    """,
    'author': "DataDialog - Michael Karrer",
    'website': "http://www.datadialog.net/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'base',
        'website_forum',
    ],
    'installable': True,
    'data': [
        'views/templates.xml',
        #'views/snippets.xml',
    ],
}