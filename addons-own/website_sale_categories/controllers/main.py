# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request

# import the base controller class to inherit from
from openerp.addons.website_sale.controllers.main import website_sale


class website_sale_categories(website_sale):
    # List only products in the same cat_root_id tree:
    def _get_search_domain(self, search, category, attrib_values):
        domain = super(website_sale_categories, self)._get_search_domain(search, category, attrib_values)
        if category:
            # 1.) Find all relevant categories (self, and children with the same cat_root_id)
            #     HINT: child_of operator will find self and childs! (so not only childs as maybe expected)
            category_obj = request.registry['product.public.category']
            child_categories = category_obj.search(request.cr, request.uid, ['&',
                                                             ('parent_id', 'child_of', int(category)),
                                                             ('cat_root_id', '=', int(category.cat_root_id))],
                                                   context=request.context)
            # 2.) Extend the product search domain to only show products which are in one or more of the categories
            domain += [('public_categ_ids', 'in', child_categories)]
        return domain
