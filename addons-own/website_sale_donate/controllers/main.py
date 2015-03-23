# -*- coding: utf-8 -*-
import logging
from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request

# To get a new db connection:
# from openerp.modules.registry import RegistryManager

# import the base controller class to inherit from
from openerp.addons.website_sale.controllers.main import website_sale

_logger = logging.getLogger(__name__)


class website_sale_donate(website_sale):
    # PRODUCT PAGE: Extend the product page render request to include price_donate and payment_interval
    # so we have the same settings for arbitrary price and payment interval as already set by the user in the so line
    # Todo: Would need to update the Java Script of Website_sale to select the correct product variante if it
    # Todo:     is already in the current sales order (like i do it for price_donate and payment_interval)
    # /shop/product/<model("product.template"):product>
    @http.route()
    def product(self, product, category='', search='', **kwargs):

        # this will basically pre-render the product page and store it in productpage
        productpage = super(website_sale_donate, self).product(product, category, search, **kwargs)

        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        sale_order_id = request.session.sale_order_id

        # Set a default payment_interval_id: will be rendered as checked in the product page
        if product.payment_interval_ids:
            productpage.qcontext['payment_interval_id'] = product.payment_interval_ids[0].id

        if sale_order_id:
            # search for a sales order line for the current product in the sales order of the current session
            sol_obj = pool['sale.order.line']
            # get sale order line id if product or variant of product is in active sale order
            sol = sol_obj.search(cr, SUPERUSER_ID,
                                 [['order_id', '=', sale_order_id],
                                  ['product_id', 'in', product.ids + product.product_variant_ids.ids]],
                                 context=context)
            if len(sol) == 1:
                # Get the sale.order.line
                sol = sol_obj.browse(cr, SUPERUSER_ID, sol[0], context=context)
                if sol.exists():

                    # Add the Arbitrary Price to the qweb template context
                    if sol.price_donate:
                        productpage.qcontext['price_donate'] = sol.price_donate

                    # Add the Payment Interval to the qweb template context
                    if sol.payment_interval_id and sol.payment_interval_id in sol.product_id.payment_interval_ids:
                        productpage.qcontext['payment_interval_id'] = sol.payment_interval_id.id

        return productpage

    # SHOPPING CART: replace the original cart update request to include **kw = all input values of the form
    # /shop/cart/update
    @http.route()
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        cr, uid, context = request.cr, request.uid, request.context

        # Pass kw to _cart_update to transfer all post variables to _cart_update
        # (This was the only problem with the original method call)
        # This is needed to get the Value of the arbitrary price from the input field
        request.website.sale_get_order(force_create=1)._cart_update(product_id=int(product_id),
                                                                    add_qty=float(add_qty),
                                                                    set_qty=float(set_qty),
                                                                    **kw)

        # If simple_checkout is set for the product redirect directly to checkout instead of cart
        if request.registry['product.product'].browse(cr, SUPERUSER_ID,
                                                      int(product_id), context=context).simple_checkout:
            return request.redirect('/shop/checkout')

        return request.redirect("/shop/cart")


    # SIMPLE CHECKOUT:
    # Add an alternative route for products to directly add them to the shopping cart and DIRECTLY go to the checkout
    # This is usefull if you want to create buttons to directly pay / donate for a product
    # HINT: We have to use product.product because otherwise we could not directly check out product variants AND
    # _cart_update expects an product.product id anyway
    @http.route(['/shop/simplecheckout/<model("product.product"):product>'], type='http', auth="public", website=True)
    def simplecheckout(self, product, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        request.website.sale_get_order(force_create=1, context=context)._cart_update(product_id=product.id,
                                                                                     add_qty=1,
                                                                                     context=context,
                                                                                     **kwargs)

        return request.redirect('/shop/checkout')


    # SET CUSTOM MANDATORY BILLING AND OR SHIPPING FIELDS:
    def checkout_parse(self, address_type, data, remove_prefix=False):

        # Set Billing Fields
        # HINT: I change the original class attributes just in case any other method uses them later.
        #       If any other method uses them before checkout parse is run it will still get the original
        #       values - so it is still poor design - but this is basically odoo's fault and not mine ;)
        website_sale.mandatory_billing_fields = []
        website_sale.optional_billing_fields = []
        bill_keys = [key.replace("_mandatory_bill", "", 1)
                     for key in request.website._fields.keys()
                     if "_mandatory_bill" in key]
        for key in bill_keys:
            if request.website[key + "_mandatory_bill"] is True:
                website_sale.mandatory_billing_fields += [key, ]
            else:
                website_sale.optional_billing_fields += [key, ]

        # Set Shipping Fields
        website_sale.mandatory_shipping_fields = []
        website_sale.optional_shipping_fields = []
        ship_keys = [key.replace("_mandatory_ship", "", 1)
                     for key in request.website._fields.keys()
                     if "_mandatory_ship" in key]
        for key in ship_keys:
            if request.website[key + "_mandatory_ship"] is True:
                website_sale.mandatory_shipping_fields += [key, ]
            else:
                website_sale.optional_shipping_fields += [key, ]

        return super(website_sale_donate, self).checkout_parse(address_type, data, remove_prefix)
