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
from openerp import SUPERUSER_ID


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
    # Topmost parent category:
    # Store the nearest parent category in the field cat_root_id  that has cat_root=True or, if no parent category has
    # cat_root set to True, set the topmost parent category for cat_root_id. Use the current category for cat_root_id if
    # no parent category is available or the current category has cat_root set to True.
    # HINT: This field is used in the category qweb-template to render the categories as well as for products shown at
    #       each category (domain filter in main.py)
    # ATTENTION: Hidden categories are treated like root categories even if root_cat is not set!
    cat_root_id = fields.Many2one(comodel_name='product.public.category',
                                  string='Nearest Root Category or UpMost Parent')

    # Update the field cat_root_id at addon installation or update
    # Todo: Test if this works at install time too an not just at addon update
    def init(self, cr, context=None):
        print "INIT OF website_sale_categories"
        allcats = self.search(cr, SUPERUSER_ID, [])
        for catid in allcats:
            cat = self.browse(cr, SUPERUSER_ID, catid)
            # To set the parent_id will trigger the recalculation of cat_root_id in the write method
            cat.write({"parent_id": cat.parent_id.id or None})


    # Recalculate the cat_root_id
    @api.multi
    def write(self, vals):
        # Write the changes (to the environment cache?) first!
        # ATTENTION: Hidden categories are treated like root categories!
        if 'cat_hide' in vals and self.ensure_one():
            if vals['cat_hide']:
                vals['cat_root'] = True
        res = super(product_public_category_menu, self).write(vals)

        # If parent_id or cat_root or cat_hide are changed calculate the cat_root_id field
        if 'parent_id' in vals or 'cat_root' in vals or 'cat_hide' in vals and self.ensure_one():

            # Calculate the cat_root_id of the current category
            cat = self
            while True:
                if cat.cat_root or cat.cat_hide or not cat.parent_id:
                    self.cat_root_id = cat.id
                    break
                else:
                    cat = cat.parent_id

            # Calculate the cat_root_id of the child categories (if any)
            categories = self.env['product.public.category'].search(['&',
                                                                     ('id', 'child_of', int(self.id)),
                                                                     ('id', 'not in', self.ids)])
            for child_cat in categories:
                cat = child_cat
                while True:
                    if cat.cat_root or cat.cat_hide or not cat.parent_id:
                        if cat.ids:
                            child_cat.cat_root_id = cat.id
                        break
                    else:
                        cat = cat.parent_id

        return res
