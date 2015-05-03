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
        'country_id_mandatory_bill': 1,
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

# HINT: Since we set this fields on product.template it is not possible to have different values for variants
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


# Extend sale.order.line to be able to store price_donate and payment interval information
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

    def _website_product_id_change(self, cr, uid, ids, order_id, product_id, qty=0, line_id=None, context=None):
        context = context or {}
        res = super(sale_order, self)._website_product_id_change(cr, uid, ids, order_id, product_id, qty=qty, line_id=line_id, context=context)
        if context.get('price_donate'):
            res.update({'price_unit': context.get('price_donate')})
        return res

    # extend _cart_update to write price_donate and payment_interval to the sale.order.line if existing in kwargs
    def _cart_update(self, cr, uid, ids, product_id=None, line_id=None, add_qty=0, set_qty=0, context=None, **kwargs):

        # Try to recalculate all functional fields on write
        context = context or {}
        context = dict(context, recompute=True)
        context = dict(context, no_store_function=True)

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

        # Update context with price_donate and call super
        price_donate = kwargs.get('price_donate')
        if price_donate:
            context.update({'price_donate': price_donate})
        cu = super(sale_order, self)._cart_update(cr, uid, ids,
                                                  product_id, line_id, add_qty, set_qty, context=context, **kwargs)
        if context.get('price_donate'):
            context.pop('price_donate', None)


        payment_interval_id = kwargs.get('payment_interval_id')
        line_id = cu.get('line_id')
        quantity = cu.get('quantity')
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
                #sol_obj.write(cr, SUPERUSER_ID, [line_id], {'price_donate': price_donate, }, context=context)

            # no matter where we come from if so line already exists and has filled price_donate field we have to
            # update the price_unit again to not loose our custom price price_donate
            if sol.price_donate:
                sol.price_unit = sol.price_donate
                #sol_obj.write(cr, SUPERUSER_ID, [line_id], {'price_unit': sol.price_donate, }, context=context)

            # TODO: Hack: for no obvious reason functional fields do net get updated on sale.order.line writes ?!? so we do it manually!
            # Sadly not working
            # sol_obj.write(cr, SUPERUSER_ID, [line_id], {'price_subtotal': sol_obj._amount_line(cr, SUPERUSER_ID, [line_id], None, None, context=context), 'price_reduce': sol_obj._get_price_reduce(cr, SUPERUSER_ID, [line_id], None, None, context=context), }, context=context)


            # If Payment Interval is found in kwargs write it to the so line
            # Todo: SECURITY Check if payment_intervall_id: is an int and if it is available in product.payment_interval
            if payment_interval_id:
                # Todo: CATCH if int conversion fails (like float above)
                sol.payment_interval_id = int(payment_interval_id)
                if sol.payment_interval_id.exists():
                    sol.payment_interval_name = sol.payment_interval_id.name
                    sol.payment_interval_xmlid = sol.payment_interval_id.get_metadata()[0]['xmlid']

            # ToDo: Try to browse and write to the sales order to update relevant fields
            # so_obj = self.pool.get('sale.order')
            # so = so_obj.browse(cr, SUPERUSER_ID, sol.order_id.id, context=context)
            # so.write(cr, SUPERUSER_ID, {}, context=context)

        return cu

    # Check if there are any recurring transaction products in the sale order
    def _has_recurring(self, cr, uid, ids, field_name, arg, context=None):
        # HINT: functional Fields have to return an dict!
        #       https://doc.odoo.com/6.0/developer/2_5_Objects_Fields_Methods/field_type/
        res = {}

        # Get th ID of payment interval with xml_id once_only to use it in the search domain
        # HINT: get_object takes the module name where the record was created and NOT the model name as expected!
        model_data_obj = self.pool.get('ir.model.data')
        pi_once_only_id = model_data_obj.get_object(cr, uid, 'website_sale_donate', 'once_only').id

        # check if we can find a related SO line with an payment interval other than None or once_only
        for order in self.browse(cr, uid, ids, context=context):
            domain = [('order_id', '=', order.id), ('payment_interval_id', '!=', pi_once_only_id)]
            if self.pool.get('sale.order.line').search(cr, SUPERUSER_ID, domain, context=context):
                res[order.id] = True
            else:
                res[order.id] = False

        return res

    _columns = {
        'has_recurring': fields.function(_has_recurring,
                                         type='boolean',
                                         string='Has order lines with recurring transactions'),
    }


# Add the field - recurring_transactions to all payment providers and an image field for icons too
# ToDo If this field is not enabled for a PP it will be hidden if there is any so line with
#      a payment_interval_id in the current shopping cart. Seems that i have to do this by java script and not by
#      the controller that renders the PP?!?
# HINT: We also add a functional field to sale_order "has_recurring_transactions" type bool - This field is true
#       if there are any recurring transaction products other than  "einmailig" which has an xml_id of
#       "once_only" in this sale.order
class PaymentAcquirer(osv.Model):
    _inherit = 'payment.acquirer'
    _columns = {
        'recurring_transactions': fields.boolean('Recurring Transactions'),
        'acquirer_icon': fields.binary("Acquirer Icon", help="Acquirer Icon 120x90 PNG 32Bit"),
    }

    _defaults = {
        'recurring_transactions': False,
    }
