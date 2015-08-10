# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    'name': "OpenAT Kundennummer",
    'version': "1.1",
    'category': "Tools",
    'summary': "openat_partnernumber_unique",
    'description': """
		Forces the Partner Number to be unique.
		Dieses Modul stellt sicher, dass die Kundennummer eindeutig ist.
		
		Field res.partner.ref is repaced by a new unique field: openat_ref_unique in the res.partner form view. In addition return a meaningfull warning if the number is already in use. This does not work if partners are generated with the quick add function or through e-mails. It only works for the save button in the res.partner form views.
		
		This Module is german only and is not translated.
		
		ATTENTION: Be carfull to show the new field openat_ref_unique in all other views and not the original field ref!
    """,
    'author': "OpenAT",
    'website': "http://www.OpenAT.at",
    'images': [],
    'depends': ['base'],
    'data': ['openat_partnernumber_unique_view.xml'],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
