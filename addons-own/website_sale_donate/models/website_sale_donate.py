# -*- coding: utf-'8' "-*-"
__author__ = 'mkarrer'

from openerp import SUPERUSER_ID
from openerp.osv import osv, orm, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


# mandatory fields setting for checkout form
class website_sale_donate_settings(osv.Model):
    _inherit = 'website'
    _columns = {
        # Billing
        'name_mandatory_bill': fields.boolean(string='name'),
        'phone_mandatory_bill': fields.boolean(string='phone'),
        'email_mandatory_bill': fields.boolean(string='email'),
        'street2_mandatory_bill': fields.boolean(string='street2'),
        'city_mandatory_bill': fields.boolean(string='city'),
        'country_id_mandatory_bill': fields.boolean(string='country_id'),
        'street_mandatory_bill': fields.boolean(string='street'),
        'state_id_mandatory_bill': fields.boolean(string='state_id'),
        'vat_mandatory_bill': fields.boolean(string='state_id'),
        'vat_subjected_mandatory_bill': fields.boolean(string='state_id'),
        'zip_mandatory_bill': fields.boolean(string='state_id'),
        # Shipping
        'name_mandatory_ship': fields.boolean(string='name'),
        'phone_mandatory_ship': fields.boolean(string='phone'),
        'street_mandatory_ship': fields.boolean(string='street'),
        'city_mandatory_ship': fields.boolean(string='city'),
        'country_id_mandatory_ship': fields.boolean(string='country_id'),
        'state_id_mandatory_ship': fields.boolean(string='state_id'),
        'zip_mandatory_ship': fields.boolean(string='street2'),
    }
    _defaults = {
        # Mandatory for billing
        'name_mandatory_bill': 1,
        'email_mandatory_bill': 1,
        # Mandatory for shipping
        'name_mandatory_ship': 1,
        'phone_mandatory_ship': 1,
        'street_mandatory_ship': 1,
        'city_mandatory_ship': 1,
        'country_id_mandatory_ship': 1,
    }


class payment_interval(osv.Model):
    _name = 'product.payment_interval'
    _columns = {
        'name': fields.text('Payment Interval', required=True, translate=True),
        'product_template_ids': fields.many2many('product.template', string='Products'),
    }

payment_interval()

# HINT: Since we set this fields on product.template it is not be possible to have different values for variants
#       of this product template (= product.product) - which is the intended use-case and ok ;)
class product_template(osv.Model):
    _inherit = "product.template"
    _columns = {
        'hide_payment': fields.boolean('Hide Add-to-Cart-Form in Product Page'),
        'hide_price': fields.boolean('Hide Price in Shop overview Pages'),
        'hide_quantity': fields.boolean('Hide Product Quantity Selector'),
        'simple_checkout': fields.boolean('Simple Checkout'),
        'price_donate': fields.boolean('Arbitrary Price'),
        'price_donate_min': fields.integer(string='Minimum Arbitrary Price'),
        'payment_interval_ids': fields.many2many('product.payment_interval', string='Payment Intervals'),
    }
    _defaults = {
        'price_donate_min': 1,
    }


# Sale order line um ein Feld price_donate erweitern
class sale_order_line(osv.Model):
    _inherit = "sale.order.line"
    _columns = {
        'price_donate': fields.float('Donate Price', digits_compute=dp.get_precision('Product Price'), ),
        'payment_interval_id': fields.many2one('product.payment_interval', string='Payment Interval ID'),
        'payment_interval_name': fields.text('Payment Interval Name'),
        'payment_interval_xmlid': fields.text('Payment Interval Name'),
    }


class sale_order(osv.Model):
    _inherit = "sale.order"

    # Todo: No strikethrough original price if current price lower than price_unit if product_donate checkbox true
    # extend _cart_update to write price_donate and payment_interval to the sale.order.line if existing in kwargs
    def _cart_update(self, cr, uid, ids, product_id=None, line_id=None, add_qty=0, set_qty=0, context=None, **kwargs):

        # Helper: Check if Argument is a Number and greater than zero
        def is_float_gtz(number=''):
            try:
                # if float conversion fails = except: return False
                # or if number is smaller than zero also return False
                if float(number) <= 0:
                    return False
                return True
            except:
                return False

        # Set the Quantity always to 1 or 0 if hide_quantity is set
        # HINT: We have to use product.product NOT product.temaplate beacuse it could be a product variant
        #       _cart_update always gets the product.product id !!! from the template!
        if self.pool.get('product.product').browse(cr, SUPERUSER_ID, product_id, context=context).hide_quantity:
            if add_qty >= 0:
                set_qty = 1
            else:
                set_qty = 0

        cu = super(sale_order, self)._cart_update(cr, uid, ids,
                                                  product_id, line_id, add_qty, set_qty, context=context, **kwargs)
        line_id = cu.get('line_id')
        quantity = cu.get('quantity')
        price_donate = kwargs.get('price_donate')
        payment_interval_id = kwargs.get('payment_interval_id')
        sol_obj = self.pool.get('sale.order.line')
        sol = sol_obj.browse(cr, SUPERUSER_ID, line_id, context=context)

        # sol.exists() is checked in case that so line was unlinked in inherited _cart_update
        if quantity > 0 and sol.exists():

            # If we come from a product page price_donate may be in the kwargs and if so we write it to so line
            # SECURITY: Make sure price_donate is some sort of float (real float conversion will be done by orm)
            # SECURITY: make sure price_donate checkbox is set in related product
            # VALIDATION: Make Sure price_donate is not lower than price_donate_min set in the product
            #             if it is lower then do not set price_donate = do not alter price_unit
            if price_donate \
                    and is_float_gtz(price_donate) \
                    and sol.product_id.price_donate \
                    and price_donate >= sol.product_id.price_donate_min:
                sol.price_donate = price_donate

            # no matter where we come from if so line already exists and has filled price_donate field we have to
            # update the price_unit again to not loose our custom price price_donate
            if sol.price_donate:
                sol.price_unit = sol.price_donate

            # If Payment Interval is found in kwargs write it to the so line
            # Todo: SECURITY Check if payment_intervall_id: is an int and if it is available in product.payment_interval
            if payment_interval_id:
                # Todo: CATCH if int conversion fails (like float above)
                sol.payment_interval_id = int(payment_interval_id)
                if sol.payment_interval_id.exists():
                    sol.payment_interval_name = sol.payment_interval_id.name
                    sol.payment_interval_xmlid = sol.payment_interval_id.get_metadata()[0]['xmlid']

        return cu