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

import time
import datetime
from dateutil.relativedelta import relativedelta

import openerp
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.tools.translate import _
from openerp.osv import fields, osv

class base_config_settings(osv.osv_memory):
    _name = "base_config.settings"
    _inherit = 'res.config.settings'
    _columns = {
        'module_base_field_serialized': fields.boolean('Adds fields of type serialized to odoo v8',
            help='Could be needed by older modules - and Aeroo Reports!'
                 '\n Installs Module: base_field_serialized'),
        'module_base_location': fields.boolean('City/Zip auto complete',
            help='Makes it easier to fill all the Data for Zip, City and State'
                 '\n Installs Module: base_location'),
        'module_base_location_geonames_import': fields.boolean('Donwload City, Zip, State Information',
            help='You could download / update City, Zip and State information!'
                 '\n Installs Module: base_location'),
        'module_dbfilter_from_header': fields.boolean('This addon lets you pass a dbfilter as a HTTP header.',
            help='This addon lets you pass a dbfilter as a HTTP header.'
                 '\n Installs Module: dbfilter_from_header'),
        'module_disable_openerp_online': fields.boolean('Disable all Spy from OpenERP SA',
            help='Removes Warning, Online Help and Online Apps'
                 '\n Installs Module: disable_openerp_online'),
        'module_mass_editing': fields.boolean('Mass Editing for any field (set and unset possible)',
            help='You could create Mass-Editing-Actions for any modell.field in odoo!'
                 '\n Installs Module: mass_editing'),
        'module_web_ckeditor4': fields.boolean('DEPRECATED! CKeditor4 for any html/text field in the odoo backend!',
            help='This is for Version 7 of odoo and is only there for development purposes.'
                 '\n Installs Module: web_ckeditor4'),
        'module_web_export_view': fields.boolean('Export any Tree-View as Excel Sheet',
            help='This tool makes the export of tree views much easier since it exports the view as seen on screen!'
                 '\n Installs Module: web_export_view'),
    }
