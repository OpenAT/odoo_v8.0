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
    'name': "OpenAT Partner Full Hierarchy",
    'version': "1.0",
    'category': "Tools",
    'summary': "openat_partner_hierarchy",
    'description': """
Enable the use of a parent partner or company for non companies also (parent_id for all).
Various enhancements for the res.partner.kanban res.partner.form and res.partner.tree views
ToDo: add a new openat_parent_id_full field to display all parents of a res.partner and not just the next level
    """,
    'author': "OpenAT",
    'website': "http://www.OpenAT.at",
	'css': [],
    'images': [],
    'depends': ['base'],
    'data': ['openat_partner_fullhierarchy.xml'],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
