# -*- coding: utf-8 -*-
##############################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
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
        'module_web_tree_many2one_clickable': fields.boolean('DO NOT INSTALL! Make many2one fields clickabe in tree views',
                                                             help='You can set a global config option to use this in any tree view - web_tree_many2one_clickable.default True'
                                                                  '\n Installs Module: web_tree_many2one_clickable'),
        'module_help_online': fields.boolean('DO NOT INSTALL! Create a help page for any odoo backend view',
                                             help='This makes it easy to create an inline help for the users of odoo'
                                                  '\n Installs Module: help_online'),
        'module_web_recipients_uncheck': fields.boolean('DO NOT INSTALL! Uncheck default receipients of chatter (e-mail)',
                                                        help='Normaly you can not untick receipients of chatter messages - this makes it possible!'
                                                             '\n Installs Module: web_recipients_uncheck'),
        'module_web_m2x_options': fields.boolean('More xml view widget options for many2x fields',
                                                 help='Adds options to hide create or create and edit for many2x fields!'
                                                      '\n Installs Module: web_m2x_options'),
        'module_email_cc_bcc': fields.boolean('DO NOT INSTALL! Add bcc and cc fields to chatter e-mails',
                                              help='Add bcc and cc fields to chatter e-mai!'
                                                   '\n Installs Module: email_cc_bcc'),
        'module_web_filter_tabs': fields.boolean('DO NOT INSTALL! Save Searches as Tabs',
                                                 help='Save Searches as Tabs'
                                                      '\n Installs Module: web_filter_tabs'),
        'module_web_group_expand': fields.boolean('DO NOT INSTALL! Unfold or Fold groups in tree views',
                                                  help='Unfold or Fold groups in tree views!'
                                                       '\n Installs Module: web_group_expand'),
        'module_project_code': fields.boolean('Add a Code to Projects',
                                              help='Add a code to project.project and make it visible and searchable!'
                                                   '\n Installs Module: project_code'),
        'module_website_search': fields.boolean('Global search box for the webpage',
                                                help='Global search box for the webpage'
                                                     '\n Installs Module: website_search'),
        'module_website_blog_private': fields.boolean('BUG! DO NOT LINK! Private (internal) blogs on website',
                                                      help='Private blogs'
                                                           '\n Installs Module: website_blog_private'),
        'module_website_forum_private': fields.boolean('BUG! DO NOT LINK! Private (internal) forums on website',
                                                       help='Private Forums'
                                                            '\n Installs Module: website_forum_private'),
        'module_website_lang_flags': fields.boolean('Language Flags for website lang selector',
                                                    help='Language Flags instead of just text for lang selector on website'
                                                         '\n Installs Module: website_lang_flags'),
        'module_website_crm_extended': fields.boolean('Default sales group for lead from contact formular',
                                                       help='Adds default sales group an lead creation from website contact formular'
                                                            '\n Installs Module: website_crm_extended'),
        'module_payment_frst': fields.boolean('FRST Payment Provider',
                                              help='Payment Provider for IBAN and BIC (Bankeinzug)'
                                                   '\n Installs Module: payment_frst'),
        'module_website_sale_donate': fields.boolean('FRST eCommerce Addons',
                                                     help='Add arbitrary price, hide amount and other features to website_sale'
                                                          '\n Installs Module: website_sale_donate'),
        'module_project_basic_extensions': fields.boolean('Basic Project Extensions',
                                                          help='A lot of small tweaks to project, tasks and issues'
                                                          '\n Installs Module: website_sale_donate'),
        'module_website_highlight_code': fields.boolean('Forum Code Highlighting',
                                                      help='Includes highlight.js and add new addons to ckeditor of forum'
                                                           '\n Installs Module: website_sale_catdesc'),
        'module_website_sale_catdesc': fields.boolean('Description for Website categories',
                                                      help='Description for Website categories shown in overview pages'
                                                           '\n Installs Module: website_sale_catdesc'),
    }
