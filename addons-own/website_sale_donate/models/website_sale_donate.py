# -*- coding: utf-'8' "-*-"
__author__ = 'mkarrer'

from openerp import SUPERUSER_ID
from openerp import tools
from openerp.osv import osv, orm, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.addons.base_tools.image import resize_to_thumbnail


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
        # Country
        'country_default_value': fields.many2one('res.country', string='Default country for checkout page'),
        # Behaviour
        'add_to_cart_stay_on_page': fields.boolean(string='Add to Cart and stay on Page'),
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

    def _get_parallax_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.parallax_image,
                                                            big_name='parallax_image',
                                                            medium_name='parallax_image_medium',
                                                            small_name='parallax_image_small',
                                                            avoid_resize_medium=True)
        return result

    def _set_parallax_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'parallax_image': value}, context=context)

    def _get_square_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            # need to return also an dict for the image like result[1] = {'image_square': base_64_data}
            result[obj.id] = {'image_square': False}
            if obj.image:
                result[obj.id] = {'image_square': resize_to_thumbnail(img=obj.image, box=(440, 440),)}
        return result

    def _set_square_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': value}, context=context)

    # OVERRIDE orignal image functional fields to store full size images
    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': value}, context=context)

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
        return result

    _columns = {
        'hide_payment': fields.boolean('Hide complete Checkout Panel'),
        'hide_price': fields.boolean('Hide Price in Shop overview Pages'),
        'hide_quantity': fields.boolean('Hide Product-Quantity-Selector in CP'),
        'simple_checkout': fields.boolean('Simple Checkout'),
        'price_donate': fields.boolean('Arbitrary Price'),
        'price_donate_min': fields.integer(string='Minimum Arbitrary Price'),
        'payment_interval_ids': fields.many2many('product.payment_interval', string='Payment Intervals'),

        'hide_search': fields.boolean('Hide Search Field'),
        'hide_categories': fields.boolean('Hide Categories Navigation'),
        'hide_image': fields.boolean('Hide Image in Checkout Panel'),
        'hide_salesdesc': fields.boolean('Hide Text in Checkout Panel'),
        'hide_panelfooter': fields.boolean('Hide Checkout Panel Footer'),

        'show_desctop': fields.boolean('Show additional Description above Checkout Panel'),
        'show_descbottom': fields.boolean('Show additional Description below Checkout Panel'),

        'desc_short_top': fields.html(string='Banner Product Description - Top'),
        'desc_short': fields.html(string='Banner Product Description - Center'),
        'desc_short_bottom': fields.html(string='Banner Product Description - Bottom'),
        'image_square': fields.function(_get_square_image, fnct_inv=_set_square_image,
            string="Square Image (Auto crop and zoom)", type="binary", multi="_get_square_image",
            store={'product.template': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10)}),
        'parallax_image': fields.binary(string='Background Parallax Image'),
        'parallax_image_medium': fields.function(_get_parallax_image, fnct_inv=_set_parallax_image,
            string="Background Parallax Image", type="binary", multi="_get_parallax_image",
            store={
                'product.template': (lambda self, cr, uid, ids, c={}: ids, ['parallax_image'], 10),
            },
            help="Medium-sized image of the background. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved, "\
                 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
        'parallax_speed': fields.selection([('static', 'Static'), ('slow', 'Slow')], string='Parallax Speed'),
        # OVERRIDE orignal image functional fields to store full size images
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image",
            store={
                'product.template': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized image of the product. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved, "\
                 "only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized image", type="binary", multi="_get_image",
            store={
                'product.template': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized image of the product. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
    }
    _defaults = {
        'price_donate_min': 0,
        'parallax_speed': 'slow',
        'hide_quantity': True,
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
        res = super(sale_order, self)._website_product_id_change(cr, uid, ids, order_id, product_id, qty=qty,
                                                                 line_id=line_id, context=context)
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
                # sol_obj.write(cr, SUPERUSER_ID, [line_id], {'price_donate': price_donate, }, context=context)

            # no matter where we come from if so line already exists and has filled price_donate field we have to
            # update the price_unit again to not loose our custom price price_donate
            if sol.price_donate:
                sol.price_unit = sol.price_donate
                # sol_obj.write(cr, SUPERUSER_ID, [line_id], {'price_unit': sol.price_donate, }, context=context)

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


# CROWD FUNDING EXTENSIONS
# ========================
class product_product(osv.Model):
    _inherit = 'product.product'

    def _sold_total(self, cr, uid, ids, field_name, arg, context=None):
        r = dict.fromkeys(ids, 0)
        domain = [
            ('state', 'in', ['waiting_date', 'progress', 'manual', 'shipping_except', 'invoice_except', 'done']),
            ('product_id', 'in', ids),
        ]
        for group in self.pool['sale.report'].read_group(cr, SUPERUSER_ID, domain, ['product_id', 'price_total'],
                                                         ['product_id'], context=context):
            r[group['product_id'][0]] = group['price_total']

        # HINT: functional fields functions have to return a dict in form of {id: value}
        return r

    def action_view_sales_sold_total(self, cr, uid, ids, context=None):
        result = self.pool['ir.model.data'].xmlid_to_res_id(cr, uid, 'sale.action_order_line_product_tree',
                                                            raise_if_not_found=True)
        result = self.pool['ir.actions.act_window'].read(cr, uid, [result], context=context)[0]
        domain = [
            ('state', 'in', ["confirmed", "done"]),
            ('product_id', 'in', ids),
        ]
        result['domain'] = str(domain)
        return result

    _columns = {
        'sold_total': fields.function(_sold_total, string='# Sold Total', type='float'),
    }


class product_template(osv.Model):
    _inherit = 'product.template'

    def _sold_total(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0)
        for template in self.browse(cr, SUPERUSER_ID, ids, context=context):
            res[template.id] = sum([p.sold_total for p in template.product_variant_ids])
        return res

    def _funding_reached(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0)
        for ptemplate in self.browse(cr, SUPERUSER_ID, ids, context=context):
            try:
                res[ptemplate.id] = int(round(ptemplate.sold_total / (ptemplate.funding_goal / 100)))
            except:
                res[ptemplate.id] = int(0)
        return res

    def action_view_sales_sold_total(self, cr, uid, ids, context=None):
        act_obj = self.pool.get('ir.actions.act_window')
        mod_obj = self.pool.get('ir.model.data')
        # find the related product.product ids
        product_ids = []
        for template in self.browse(cr, uid, ids, context=context):
            product_ids += [x.id for x in template.product_variant_ids]
        domain = [
            ('state', 'in', ["confirmed", "done"]),
            ('product_id', 'in', product_ids),
        ]
        # get the tree view
        result = mod_obj.xmlid_to_res_id(cr, uid, 'sale.action_order_line_product_tree', raise_if_not_found=True)
        result = act_obj.read(cr, uid, [result], context=context)[0]
        # add the search domain
        result['domain'] = str(domain)
        return result

    # Hack because i could not find a way to browse res.partner.name in qweb template - always error 403 access rights
    # The positive side effect is better security since no one can browse res.partner fully!
    def _get_name(self, cr, uid, ids, flds, args, context=None):
        res = dict.fromkeys(ids, 0)
        for ptemplate in self.browse(cr, SUPERUSER_ID, ids, context=context):
            if ptemplate.funding_user:
                res[ptemplate.id] = ptemplate.funding_user.name
            else:
                res[ptemplate.id] = False
        return res

    _columns = {
        'sold_total': fields.function(_sold_total, string='# Sold Total', type='float'),
        'funding_goal': fields.float(string='Funding Goal'),
        'funding_desc': fields.html(string='Funding Description (HTML Field below Bar)'),
        'funding_reached': fields.function(_funding_reached, string='Funding reached in %', type='integer'),
        'funding_user': fields.many2one('res.partner', string='Funding-Campaign User'),
        'funding_user_name': fields.function(_get_name, string="Funding-Campaign User Name", type='char'),

        'hide_fundingtextinlist': fields.boolean('Hide Funding-Text in Overview-Pages'),
        'hide_fundingbarinlist': fields.boolean('Hide Funding-Bar in Overview-Pages'),
        'hide_fundingtextincp': fields.boolean('Hide Funding-Text in Checkout-Panel'),
        'hide_fundingbarincp': fields.boolean('Hide Funding-Bar in Checkout-Panel'),
        'hide_fundingtext': fields.boolean('Hide Funding-Text in Page'),
        'hide_fundingbar': fields.boolean('Hide Funding-Bar in Page'),
        'hide_fundingdesc': fields.boolean('Hide Funding-Description in Page'),
    }
