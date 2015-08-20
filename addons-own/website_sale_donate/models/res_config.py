from openerp.osv import fields, osv


class website_sale_donate_config_settings(osv.osv_memory):
    _inherit = 'website.config.settings'

    _columns = {
        # HINT: in addon website in res_config.py
        # 'website_id': fields.many2one('website', string="website", required=True),
        # defaults={'website_id': lambda self,cr,uid,c: self.pool.get('website').search(cr, uid, [], context=c)[0],}
        #
        # Mandatory Billing Fields (will be written to model website)
        'name_mandatory_bill': fields.related('website_id',
                                              'name_mandatory_bill', type="boolean", string='name'),
        'phone_mandatory_bill': fields.related('website_id',
                                               'phone_mandatory_bill', type="boolean", string='phone'),
        'email_mandatory_bill': fields.related('website_id',
                                               'email_mandatory_bill', type="boolean", string='email'),
        'street2_mandatory_bill': fields.related('website_id',
                                                 'street2_mandatory_bill', type="boolean", string='street2'),
        'city_mandatory_bill': fields.related('website_id',
                                              'city_mandatory_bill', type="boolean", string='city'),
        'country_id_mandatory_bill': fields.related('website_id',
                                                    'country_id_mandatory_bill', type="boolean", string='country_id'),
        # street is used for the company in template ?!? bug or indendet?
        'street_mandatory_bill': fields.related('website_id',
                                                'street_mandatory_bill', type="boolean", string='street'),
        'state_id_mandatory_bill': fields.related('website_id',
                                                  'state_id_mandatory_bill', type="boolean", string='state'),
        'vat_mandatory_bill': fields.related('website_id',
                                             'vat_mandatory_bill', type="boolean", string='vat'),
        'vat_subjected_mandatory_bill': fields.related('website_id',
                                                       'vat_subjected_mandatory_bill', type="boolean",
                                                       string='vat_subjected'),
        'zip_mandatory_bill': fields.related('website_id',
                                             'zip_mandatory_bill', type="boolean", string='zip'),
        # Mandatory Shipping Fields (will be written to model website)
        'name_mandatory_ship': fields.related('website_id',
                                              'name_mandatory_ship', type="boolean", string='name'),
        'phone_mandatory_ship': fields.related('website_id',
                                               'phone_mandatory_ship', type="boolean", string='phone'),
        'street_mandatory_ship': fields.related('website_id',
                                                'street_mandatory_ship', type="boolean", string='street'),
        'city_mandatory_ship': fields.related('website_id',
                                              'city_mandatory_ship', type="boolean", string='city'),
        'country_id_mandatory_ship': fields.related('website_id',
                                                    'country_id_mandatory_ship', type="boolean", string='country_id'),
        'state_id_mandatory_ship': fields.related('website_id',
                                                  'state_id_mandatory_ship', type="boolean", string='state_id'),
        'zip_mandatory_ship': fields.related('website_id',
                                             'zip_mandatory_ship', type="boolean", string='zip'),
        # Force Default Country  (If GeoIP is NOT working and user did not select any country)
        'country_default_value': fields.related('website_id', 'country_default_value', type="many2one",
                                                relation="res.country", string="Default country for checkout page",
                                                help="Only used if GEO IP is NOT working and user did not select any country"),
        # Behaviour
        'add_to_cart_stay_on_page': fields.related('website_id', 'add_to_cart_stay_on_page', type="boolean",
                                                   string='Add to Cart and stay on the Page'),
    }
