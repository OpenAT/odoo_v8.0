# -*- coding: utf-8 -*-
##############################################################################
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
    'name': 'FCOM website_forum_doc_fix',
    'category': 'Website',
    'summary': 'Fix bugs in Documentation addon of odoo',
    'version': '1.0',
    'description': """
website_forum_doc_fix
=====================

- Fix Controller @http.route('/forum/<model("forum.forum"):forum>/promote_ok' to get correct documentation_stage_id
- Fix template to show Promote to TOC link
- Todo: Fix Views of Posts to show content also.
- ToDo: Fix Navigation of Documentation

        """,
    'author': 'Datadialog, Michael Karrer <michael.karrer@datadialog.net>',
    'depends': [
        'website_forum',
        'website_forum_doc',
    ],
    'data': [
        'views/website_doc.xml',
    ],
    'installable': True,
}
