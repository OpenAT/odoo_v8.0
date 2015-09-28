# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-Today OpenERP SA (<http://www.openerp.com>).
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

from openerp import tools
from openerp import api, models, fields


# Extend the Product Public Category model with two new fields:
# desc = Category Description displayed in product list views
# productinfo = Additional information displayed on product pages for this category
class product_public_category_menu(models.Model):
    _inherit = 'product.public.category'

    cat_css_showatchilds = fields.Text(string="CSS used at this and its Child Categories")

    cat_desc_showatchilds = fields.Html(string="Top-Description shown at Child Categories")
    cat_desc = fields.Html(string="Top-Category-Description")

    cat_descbottom_showatchilds = fields.Html(string="Bottom-Description shown at Child Categories")
    cat_descbottom = fields.Html(string="Bottom-Category-Description")

    cat_hide = fields.Boolean(string="Hide Category from Navigation")
    cat_root = fields.Boolean(string="Start Navigation from this Category")
    # Topmost parten category -
    # if any cat_root categories are found in the tree use the topmost category with cat_root=true ans stop there
    cat_root_id = fields.Many2one(compute='_compute_root',
                                  comodel_name='product.public.category',
                                  string='Topmost Root Category')

    #@api.depends('name', 'cat_root')
    @api.multi
    def _compute_root(self):
        # find the highest parent with cat_root = True (or self if self has cat_root=True and no higher cat_root exits)
        # or just the topmost parent if no category with cat_root exists (or self if no parent exists)
        for record in self:

            cat = record
            rootcat = False
            while True:
                if cat.cat_root:
                    rootcat = cat
                if cat.parent_id:
                    cat = cat.parent_id
                else:
                    break

            if rootcat:
                record.cat_root_id = rootcat
            else:
                record.cat_root_id = cat
