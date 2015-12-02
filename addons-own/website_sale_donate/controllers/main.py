# -*- coding: utf-8 -*-
import logging
from openerp import SUPERUSER_ID
from openerp import http
from openerp.tools.translate import _
from openerp.http import request

# To get a new db connection:
# from openerp.modules.registry import RegistryManager

# import the base controller class to inherit from
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.website_sale.controllers.main import QueryURL

_logger = logging.getLogger(__name__)


class website_sale_donate(website_sale):

    # SHOP PAGE: Add last_shop_page to the session
    @http.route()
    def shop(self, page=0, category=None, search='', **post):
        request.session['last_shop_page'] = request.httprequest.base_url + '?' + request.httprequest.query_string
        request.session['last_page'] = request.session['last_shop_page']
        return super(website_sale_donate, self).shop(page=page, category=category, search=search, **post)

    # PRODUCT PAGE: Extend the product page render request to include price_donate and payment_interval
    # so we have the same settings for arbitrary price and payment interval as already set by the user in the so line
    # Todo: Would need to update the Java Script of Website_sale to select the correct product variante if it
    #       is already in the current sales order (like i do it for price_donate and payment_interval)
    # /shop/product/<model("product.template"):product>
    @http.route()
    def product(self, product, category='', search='', **kwargs):

        # Store the current request url in the session for possible returns
        # INFO: html escaping is done by request.redirect so not needed here!
        query = {'category': category, 'search': search}
        query = '&'.join("%s=%s" % (key, val) for (key, val) in query.iteritems() if val)
        request.session['last_page'] = request.httprequest.base_url + '?' + query

        cr, uid, context = request.cr, request.uid, request.context

        # this will basically pre-render the product page and store it in productpage
        productpage = super(website_sale_donate, self).product(product, category, search, **kwargs)

        # Product Qweb Template based on the product_page_template field
        # HINT: qcontext hold the initial values the qweb template was called with
        if product.product_page_template:
            productpage = request.website.render(product.product_page_template, productpage.qcontext)

        # Add Warnings (e.g. by cart_update)
        productpage.qcontext['warnings'] = kwargs.get('warnings')
        kwargs['warnings'] = None

        # Set a default payment_interval_id: will be rendered as checked in the product page
        if product.payment_interval_ids:
            productpage.qcontext['payment_interval_id'] = product.payment_interval_ids[0].id

        # Get values from sales order line
        sale_order_id = request.session.sale_order_id
        if sale_order_id:
            # Search for a sales order line for the current product in the sales order of the current session
            sol_obj = request.registry['sale.order.line']
            # Get sale order line id if product or variant of product is in active sale order
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

    # SHOPPING CART: add keep to the values of qcontext
    # /shop/cart
    @http.route()
    def cart(self, **post):
        cartpage = super(website_sale_donate, self).cart(**post)
        cartpage.qcontext['keep'] = QueryURL(attrib=request.httprequest.args.getlist('attrib'))
        return cartpage

    # SIMPLE CHECKOUT:
    # Add an alternative route for products to directly add them to the shopping cart and DIRECTLY go to the checkout
    # This is useful if you want to create buttons to directly pay / donate for a product
    # HINT: We have to use product.product because otherwise we could not directly check out product variants AND
    #       _cart_update expects an product.product id anyway
    @http.route(['/shop/simplecheckout/<model("product.product"):product>',
                 '/shop/simple_checkout/<model("product.product"):product>'],
                auth="public", website=True)
    def simple_checkout(self, product, **kw):
        kw.update(simple_checkout=True)
        return self.cart_update(product, **kw)

    # SHOPPING CART UPDATE
    # /shop/cart/update
    @http.route(['/shop/cart/update'])
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        cr, uid, context = request.cr, request.uid, request.context

        product = request.registry['product.product'].browse(cr, SUPERUSER_ID, int(product_id), context=context)

        # Validate (donation) Arbitrary Price
        warnings = None
        price = kw.get('price_donate') or product.list_price or product.price
        # HINT: If price_donate is not a valid number it will be empty and so the product.list_price is used!
        #       Therefore the try statement is not really needed (but kept for safety).
        try:
            if product.price_donate_min and float(product.price_donate_min) > float(price):
                warnings = _('Value must be higher or equal to %s.' % float(product.price_donate_min))
        except ValueError:
            warnings = _('Value must be a valid Number.')
            pass
        if warnings:
            return request.redirect('/shop/product/%s?&warnings=%s' % (product.product_tmpl_id.id, warnings))

        # Check Payment Interval
        # INFO: This is only needed if products are directly added to cart on shop pages (product listings)
        if 'payment_interval_id' not in kw:
            if product.payment_interval_ids:
                kw['payment_interval_id'] = product.payment_interval_ids[0].id

        # Call Super
        # INFO: Pass kw to _cart_update to transfer all post variables to _cart_update
        #       This is needed to get the Value of the arbitrary price from the input field
        request.website.sale_get_order(force_create=1, context=context)._cart_update(product_id=int(product_id),
                                                                                     add_qty=float(add_qty),
                                                                                     set_qty=float(set_qty),
                                                                                     context=context,
                                                                                     **kw)

        # If simple_checkout is set for the product redirect directly to checkout or confirm_order
        if product.simple_checkout or kw.get('simple_checkout'):
            kw.pop('simple_checkout', None)
            if kw.get('email') and kw.get('name') and kw.get('shipping_id'):
                return request.redirect('/shop/confirm_order' + '?' + request.httprequest.query_string)
            return request.redirect('/shop/checkout' + '?' + request.httprequest.query_string)

        # Stay on the current page if "Add to cart and stay on current page" is set
        if request.session.get('last_page') and request.website['add_to_cart_stay_on_page']:
            return request.redirect(request.session['last_page'])

        # Redirect to the shopping cart
        return request.redirect("/shop/cart")


    # Set mandatory billing and shipping fields
    # HINT: All possible fields are added to the website object as boolean fields in
    #       website_sale_donate.py -> website_sale_donate_settings with a naming convention of
    #       _mandatory_bill and _mandatory_ship
    # HINT: Possible since odoo commit
    #       https://github.com/odoo/odoo/commit/4f41c3327c40d3fbbd219dad732a98d09d52bd30
    def _get_mandatory_billing_fields(self):
        return [key.replace("_mandatory_bill", "", 1)
                for key in request.website._fields.keys()
                if "_mandatory_bill" in key and request.website[key] is True]

    def _get_optional_billing_fields(self):
        return [key.replace("_mandatory_bill", "", 1)
                for key in request.website._fields.keys()
                if "_mandatory_bill" in key and request.website[key] is False]

    def _get_mandatory_shipping_fields(self):
        return [key.replace("_mandatory_ship", "", 1)
                for key in request.website._fields.keys()
                if "_mandatory_ship" in key and request.website[key] is True]

    def _get_optional_shipping_fields(self):
        return [key.replace("_mandatory_ship", "", 1)
                for key in request.website._fields.keys()
                if "_mandatory_ship" in key and request.website[key] is False]
