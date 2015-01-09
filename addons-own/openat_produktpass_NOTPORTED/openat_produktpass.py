# -*- coding: utf-8 -*-
# #############################################################################
#
# OpenAT
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import datetime
from datetime import datetime

import openerp
from openerp import SUPERUSER_ID, api
from openerp.osv import fields, osv, expression
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round


class res_partner(osv.Model):
    _inherit = 'res.partner'
    _columns = {
        'openat_produktpass_ids': fields.many2many('product.product',
                                                   'produktpass_partner_rel', 'partner_id', 'produktpass_id',
                                                   string='Product Passes'),
    }


res_partner()


class product_template(osv.Model):
    # Ist mir noch unklar wie die Inheritance hier funktioniert - des is scho speziell - denke aber das es sich hier
    # um eine art super init handelt das in osv.Model stattfindet?!? - to be found
    _inherit = 'product.template'

    def __init__(self, cr, uid):
        # Super ist mir noch suspekt die frage ist ob man das auch so schreiben koennte
        # dieser schritt bedeutet meiner Meinung nach nix anderes als das eben in unserem erweiterten init zuerst der
        # __init__ originalen Klasse ausgefuehrt wird.
        super(product_template, self).__init__(cr, uid)

        # Versuch 1 Fuehrt leider zu recursion ?!?
        # Wahrscheinlich da die beiden klassen den selben namen haben also es sich eben nicht um eine ableitung
        # der originalen klasse handelt sondern eben um ein ueberschreiben
        #product_template.__init__(self, cr, uid)

        # Nach dem init der Originalen Klasse ueberschreiben wir gleich ein paar seiner attribute - im speziellen
        # den inhalt des state wertes des dictionaries _columns. Da der Wert von state wiederum ein eigenes objekt ist
        # naemlich ein fields.selection Objekt muessen wir auf dieses wie folgt zugreifen
        # fields.selection.selection -> das bedeutet also _columns['state'].selection
        # da in _columns['state'] das Objekt fields.selection "zugewiesen" ist
        # das objekt fields.selection hat ein attribut namens selection in dem die selection list enthalten ist
        # Deshalb kommt da auch eine Liste zurueck und nicht das objekt ;)

        # leere Elemente loeschen
        self._columns['state'].selection = [x for x in self._columns['state'].selection if x != ('', '')]

        # neue Elemente anhaengen
        for newstate in [('ppnew', 'New'), ('pptocheck', 'To Check'), ('ppapproved', 'Approved')]:
            if newstate not in self._columns['state'].selection:
                self._columns['state'].selection.append(newstate)


product_template()


class product_product(osv.Model):
    _name = 'product.product'
    _inherit = 'product.product'
    '''
    Function for Function Fields: Used to get the import date and user from ir.model.data for each product.product
    where an external id record exists.
    We can use one function for both fields because the calling field name is in field_name call of method
    !!! Therefore make sure the field field_name exists (has the same name) in ir.model.data and product.product!!!
    '''
    def _get_irmodeldata(self, cr, uid, ids, field_name, arg, context=None):
        print '_get_irmodeldata -> ids: %s' % ids
        irmodeldata = self.pool.get('ir.model.data')
        irmodeldata_records = irmodeldata.read(cr,
                                               uid,
                                               irmodeldata.search(cr,
                                                                  uid,
                                                                  [('model', '=', 'product.product'),
                                                                   ('res_id', 'in', ids)],
                                                                  context=context),
                                               context=context)
        '''
        es ist nicht sicher das auch fuer jede der ids die suche ein ergebniss liefert aber im suchergebniss
        sind bereits beide wichtigen felder enthalten res_id und field_name (z.B.: date_init)
        [{'res_id': 43, 'date_init': '2014-07-24 22:03:07'}, {'res_id': 43, 'date_init': '2014-07-24 22:03:07'}]
        nun muss die liste mit den dicst noch in ein reines dict umgewandelt werden
        '''
        print '_get_irmodeldata -> irmodeldata_records: %s' % irmodeldata_records
        ret = {record['res_id']: record[field_name] for record in irmodeldata_records if record['res_id']}
        print 'Import Date: ret: %s' % ret
        return ret

    # Return all partner_ids (res.user) from partnerlines in openat_partnerlines_ids for given records
    def _get_partner_ids(self, cr, uid, ids, field_name, arg, context=None):
        ret = {}
        partnerlines = self.pool.get('openat_produktpass.partnerlines')
        partnerlines_results = partnerlines.read(cr, uid,
                                                 partnerlines.search(cr, uid,
                                                                     [('openat_produktpass_id', 'in', ids)],
                                                                     context=context),
                                                 context=context)
        #[{'id': 19, 'openat_partner_id': (8, u'Firma A'), 'openat_produktpass_id': (43, u'Dicke Braune'), 'name': u'Alt Name A'},
        # {'id': 20, 'openat_partner_id': (9, u'Firma B'), 'openat_produktpass_id': (43, u'Dicke Braune'),
        # ...]
        print "_get_partner_ids() partnerlines_results: %s " % partnerlines_results
        if partnerlines_results:
            for id in ids:
                user_ids = [item['openat_partner_id'][0] for item in partnerlines_results if item['openat_produktpass_id'][0] == id]
                if user_ids:
                    ret[id] = user_ids
        return ret

    def _search_partner_ids(self, cr, uid, obj, name, args, context=None):
        print "_search_partner_ids() -------------------------------------------"
        print "_search_partner_ids() obj, name, args: %s, %s, %s " % (obj, name, args)
        print "_search_partner_ids() context: %s" % context
        # Ich moechte dann jeden pp der in seinen partnerlines einen res.user mit der id 8 hat
        # kann = oder ilike sein :(
        # SChritt 1 openat_partnerlines_ids ersetzen durch openat_partner_id
        # ich kenne die partner ids oder den ilike partner namen
        res=[]
        partnerlines = self.pool.get('openat_produktpass.partnerlines')
        partnerlines_results = partnerlines.read(cr, uid,
                                                 partnerlines.search(cr, uid,
                                                                     [('openat_partner_id', args[0][1], args[0][2])],
                                                                     context=context),
                                                 context=context)
        res = [partnerline['openat_produktpass_id'][0] for partnerline in partnerlines_results
               if partnerline['openat_produktpass_id'][0]]
        print "_search_partner_ids() res: %s " % res
        print "_search_partner_ids() -------------------------------------------"
        return [('id', 'in', res)]

    _columns = {
        # Access Fields
        'create_uid': fields.many2one('res.users', 'Created by', readonly=True),
        'create_date': fields.datetime('Creation Date', readonly=True),
        'write_uid': fields.many2one('res.users', 'Changed by', readonly=True),
        'write_date': fields.datetime('Change Date', readonly=True),
        # Import Fields
        'date_init': fields.function(_get_irmodeldata,
                                     store=True,
                                     #store={'product.product': (_get_irmodeldata, ['date_init'], 10)},
                                     string='First Import Date', type='datetime', readonly=True),
        'user_init': fields.many2one('res.users', 'First Import by', readonly=True),
        'date_update': fields.function(_get_irmodeldata,
                                       store=True,
                                       #store={'product.product': (_get_irmodeldata, ['date_update'], 10)},
                                       string='Last Import Date', type='datetime', readonly=True),
        # set at import because of the load class overwritten for openat_produktpass
        'user_update': fields.many2one('res.users', 'Last Import by', readonly=True),
        # Should be set in the import CSV File:
        'csb_data_date': fields.datetime('CSB-Data from', type='datetime'),
        'nuts_data_date': fields.datetime('Nuts-Data from', type='datetime'),
        # Approved by user at date - Auto set through Button Approved
        'approved_user': fields.many2one('res.users', 'Approved by', readonly=True),
        'approved_date': fields.datetime('Approved Date', type='datetime', readonly=True),
        # Nuts Data Manager and NUTS Approved Date - if set it means that it was checked at that day!
        # TODO: Must be a Button and fields read only to avoid manipulation!
        'nuts_manager': fields.many2one('res.users', 'Nuts Data Manager'),
        'nuts_approved_user': fields.many2one('res.users', 'Nuts Approved by', readonly=True),
        'nuts_approved_date': fields.datetime('Nuts Approved Date', type='datetime', readonly=True),
        #
        #'openat_kunden_ids': fields.many2many('res.partner',
        #                                      'produktpass_partner_rel', 'produktpass_id', 'partner_id',
        #                                      string='Kunden'),
        #
        # Partner Lines
        'openat_partnerlines_ids': fields.one2many('openat_produktpass.partnerlines', 'openat_produktpass_id',
                                                  'Partner Article Name'),
        'openat_partnerlines_partner_ids': fields.function(
            _get_partner_ids,
            fnct_search=_search_partner_ids,
            obj="res.partner",
            string='Partner', type='one2many', readonly=True),
        #
        'openat_csb_nummer': fields.char('CSB Article ID', size=64, required=True, translate=False, readonly=True,
                                         states={'ppnew': [('required', False), ('readonly', False)]}),
        'openat_bezeichnung': fields.char('Article Name', translate=True),
        # Markennamen sollen als Tags geloest werden
        'openat_markenname_ids': fields.many2many('openat_produktpass.markenname', string='Brand Names'),
        # Warengruppe = Produktgruppe - To Be Tested
        # Warenuntergruppe wird ebenfalls ueber Produktgruppe geregelt - To Be Tested
        'openat_verkehrsbezeichnung': fields.char('Trading Name', translate=True),
        # Produktfoto - Feld Bereits vorhanden
        'openat_ean_verkauf': fields.char('EAN-CODE Unit of Sale', translate=False),
        'openat_ean_bestell': fields.char('EAN-CODE Order Unit', translate=False),

        # LOGISTIKTDATEN - die meisten Felder bereits da - muss nur in neue Views gut uebertragen werden ;)
        # Originale Felder beachten z.B.: weight_net! Es muss dennoch andere geben weil typ char fuer z.B.: > 5
        'openat_nettofuellgewicht': fields.char('Net Fill Weight (g)'),
        'openat_tara': fields.char('Tara (g)'),
        'openat_bruttofuellgewicht': fields.char('Gross Fill Weight (g)'),

        'openat_referenzprodukte': fields.text('Reference Products', translate=True),
        #'openat_produktionsstaette': fields.text('Production Facility', translate=True),
        'openat_produktionsstaette': fields.many2one('res.partner', 'Production Facility'),
        # Lager und Transport Anweisung
        'openat_lagerundtransport_id': fields.many2one('openat_produktpass.lagerundtransport',
                                                       'Storage / Transport Instructions'),
        'openat_temperatur': fields.related('openat_lagerundtransport_id', 'openat_temperatur',
                                            type='integer', relation='openat_produktpass.lagerundtransport',
                                            string="Temperature", readonly="1"),
        'openat_luftfeuchte': fields.related('openat_lagerundtransport_id', 'openat_luftfeuchte',
                                             type='integer', relation='openat_produktpass.lagerundtransport',
                                             string="Humidity", readonly="1"),
        'openat_licht': fields.related('openat_lagerundtransport_id', 'openat_licht',
                                       type='text', relation='openat_produktpass.lagerundtransport',
                                       string="Lighting Conditions", readonly="1"),
        'openat_lageranweisung': fields.related('openat_lagerundtransport_id', 'openat_lageranweisung',
                                                type='text', relation='openat_produktpass.lagerundtransport',
                                                string="Storage Instructions", readonly="1"),
        'openat_lieferanweisung': fields.related('openat_lagerundtransport_id', 'openat_lieferanweisung',
                                                 type='text', relation='openat_produktpass.lagerundtransport',
                                                 string="Transport Instructions", readonly="1"),
        'openat_lt_beschreibung': fields.related('openat_lagerundtransport_id', 'openat_licht',
                                                 type='text', relation='openat_produktpass.lagerundtransport',
                                                 string="Storage and Transport Method Description", readonly="1"),
        # Konservierungsmethode
        'openat_konservierungsmethode_id': fields.many2one('openat_produktpass.konservierungsmethode',
                                                           'Preservation Method'),
        'openat_temp': fields.related('openat_konservierungsmethode_id', 'openat_temp',
                                      type='integer', relation='openat_produktpass.konservierungsmethode',
                                      string="Temperature (°C)", readonly="1"),
        'openat_zeit': fields.related('openat_konservierungsmethode_id', 'openat_zeit',
                                      type='char', relation='openat_produktpass.konservierungsmethode',
                                      string="Time", readonly="1"),
        'openat_schutzbegasung': fields.related('openat_konservierungsmethode_id', 'openat_schutzbegasung',
                                                type='char', relation='openat_produktpass.konservierungsmethode',
                                                string="Protective Gas", readonly="1"),
        'openat_gaszusammensetzung': fields.related('openat_konservierungsmethode_id', 'openat_gaszusammensetzung',
                                                    type='text', relation='openat_produktpass.konservierungsmethode',
                                                    string="Gas Types", readonly="1"),
        'openat_km_beschreibung': fields.related('openat_konservierungsmethode_id', 'openat_beschreibung',
                                                 type='text', relation='openat_produktpass.konservierungsmethode',
                                                 string="Description", readonly="1"),
        #
        # ersetzt durch life_time
        #'openat_mindesthaltbarkeitsdauer': fields.integer('Expiry (days)'),
        # ersetzt durch use_time
        #'openat_restlaufzeit': fields.integer('Remaining Life (days)'),
        #
        'openat_zutatenliste': fields.text('Ingredients', translate=True),
        # Naehrwerte big 7 pro 100g
        'openat_brennwert_kj': fields.char('Calorific Value (kJ)*'),
        'openat_brennwert_kcal': fields.char('Calorific Value (kcal)*'),
        'openat_fett': fields.char('Fat (g)*'),
        'openat_gesaettigte_fettsauren': fields.char('Saturated Fatty Acids (g)*'),
        'openat_einfach_ungesaettigte_fettsauren': fields.char('Monounsaturated Fatty Acids (g)'),
        'openat_mehrfach_ungesaettigte_fettsauren': fields.char('Polyunsaturated Fatty Acids (g)'),
        'openat_kohlenhydrate': fields.char('Carbohydrates (g)*'),
        'openat_kohlenhydrate_zucker': fields.char('Carbohydrates Sugar (g)*'),
        'openat_ballaststoffe': fields.char('Dietary Fibre (g)'),
        'openat_eiweiss': fields.char('Protein (g)*'),
        'openat_salz': fields.char('Salt (g)*'),
        'openat_be': fields.char('BE'),
        # Allergene EU (bolean - writeable nur wenn angehakt - onchange)
        'openat_allergene_getreide': fields.boolean('Glutenhaltiges Getreide sowie daraus hergestellte Erzeugnisse'),
        'openat_allergene_getreide_text': fields.text('Glutenhaltiges Getreide sowie daraus hergestellte Erzeugnisse',
                                                      translate=True),
        'openat_allergene_krebstiere': fields.boolean('Krebstiere u. -erzeugnisse'),
        'openat_allergene_krebstiere_text': fields.text('Krebstiere u. -erzeugnisse', translate=True),
        'openat_allergene_weichtiere': fields.boolean('Weichtiere u. -erzeugnisse'),
        'openat_allergene_weichtiere_text': fields.text('Weichtiere u. -erzeugnisse', translate=True),
        'openat_allergene_ei': fields.boolean('Ei u. -erzeugnisse'),
        'openat_allergene_ei_text': fields.text('Ei u. -erzeugnisse', translate=True),
        'openat_allergene_fisch': fields.boolean('Fisch u. - erzeugnisse'),
        'openat_allergene_fisch_text': fields.text('Fisch u. - erzeugnisse', translate=True),
        'openat_allergene_erdnuesse': fields.boolean('Erdnuesse u. -erzeugnisse'),
        'openat_allergene_erdnuesse_text': fields.text('Erdnuesse u. -erzeugnisse', translate=True),
        'openat_allergene_soja': fields.boolean('Soja u. -erzeugnisse'),
        'openat_allergene_soja_text': fields.text('Soja u. -erzeugnisse', translate=True),
        'openat_allergene_milch': fields.boolean('Milch u. -erzeugnisse '),
        'openat_allergene_milch_text': fields.text('Milch u. -erzeugnisse ', translate=True),
        'openat_allergene_schalenf': fields.boolean('Schalenfruechte u. -erzeugnisse'),
        'openat_allergene_schalenf_text': fields.text('Schalenfruechte u. -erzeugnisse', translate=True),
        'openat_allergene_lupine': fields.boolean('Lupine u. -erzeugnisse'),
        'openat_allergene_lupine_text': fields.text('Lupine u. -erzeugnisse', translate=True),
        'openat_allergene_sellerie': fields.boolean('Sellerie u. - erzeugnisse'),
        'openat_allergene_sellerie_text': fields.text('Sellerie u. - erzeugnisse', translate=True),
        'openat_allergene_senf': fields.boolean('Senf u. - erzeugnisse'),
        'openat_allergene_senf_text': fields.text('Senf u. - erzeugnisse', translate=True),
        'openat_allergene_sesam': fields.boolean('Sesamsamen u. -erzeugnisse'),
        'openat_allergene_sesam_text': fields.text('Sesamsamen u. -erzeugnisse', translate=True),
        'openat_allergene_so2_sulfite': fields.boolean('SO2 u. Sulfite [c > 10 mg/kg od. 10 mg/L as SO2]'),
        'openat_allergene_so2_sulfite_text': fields.text('SO2 u. Sulfite [c > 10 mg/kg od. 10 mg/L as SO2]',
                                                         translate=True),
        # Die richtige Kennzeichnung wird ausgwaehlt
        'openat_kennzeichnung_id': fields.many2one('openat_produktpass.kennzeichnung',
                                                   'Austrian Labeling'),
        'openat_auslobungen': fields.text('Additional Labelings', translate=True),
        'openat_rohstoffe': fields.text('Other Ingredients / Details', translate=True),
        # Chemische Analysewerte
        'openat_chem_wasser': fields.char('Water (%/100g)'),
        'openat_chem_wasser_kodex': fields.char('Water (%/100g) Minimum'),
        'openat_chem_fett': fields.char('Fat (%/100g)'),
        'openat_chem_fett_kodex': fields.char('Fat (%/100g) Minimum'),
        'openat_chem_eiweiss': fields.char('Protein (%/100g)'),
        'openat_chem_eiweiss_kodex': fields.char('Protein (%/100g) Minimum'),
        'openat_chem_kohlenhydrate': fields.char('Carbohydrates (%/100g)'),
        'openat_chem_kohlenhydrate_kodex': fields.char('Carbohydrates (%/100g) Minimum'),
        # Mikrobiologischen Grenzwerte in KBE / g
        'openat_mikrob_id': fields.many2one('openat_produktpass.mikrob', 'Microbiological Limits KBE/g'),
        # Zubereitung
        'openat_zubereitungshinweise': fields.text('Cooking', translate=True),
        # Gensusstauglichkeitskennzeichen
        'openat_genusstauglichkeitskennzeichen_id': fields.many2one('openat_produktpass.genusstauglichkeitskennzeichen',
                                                                    'Genusstauglichkeitskennzeichen'),
        'openat_zertifikate_ids': fields.many2many('openat_produktpass.zertifikate', 'rel_produktpass_zertifikate',
                                                   'openat_produktpass_id', 'openat_zertifikat_id',
                                                   'Certificates'),
        # DISPLAY
        'openat_display': fields.boolean('Display'),
        'openat_display_ids': fields.one2many('openat_produktpass.display', 'produktpass_id', 'Displaysortierung'),
    }
    _defaults = {
        'state': 'ppnew',
    }
    _sql_constraints = [('openat_csb_nummer_unique', 'unique(openat_csb_nummer)', 'CSB Article ID has to be unique!')]

    def check_valid_call(self, cr, uid, ids, context=None):
        productpass = self.read(cr, uid, ids, ['openat_csb_nummer'], context=context)
        if not len(productpass) == 1:
            raise osv.except_osv(
                'None or more than one record found!',
                'Please make sure there is only one Produkt Pass (product.product record) selected'
            )
        if not productpass[0]['openat_csb_nummer']:
            raise osv.except_osv(
                'No CSB Number!',
                'Please assign a valid CSB Number to your Product Pass (product.product.openat_csb_nummer)'
            )
        return True


    def csbnummer_to_external_id(self, cr, uid, ids, context=None, forcecsbnumber=0):
        context = context or {}
        if type(ids) is not list:
            print 'IDS BEFORE conversion to list type: %s' % ids
            ids = [ids]
        print "--------------------------------------------------------"
        print "csbnummer_to_external_id(): START"
        print "--------------------------------------------------------"
        print 'UID: %s' % uid
        print 'IDS: %s' % ids
        print 'Context: %s' % context
        #print 'Alle Attribute von product.product: %s' % dir(self)
        #print '---'

        # Read the field openat_csb_nummer for the given ids
        # The Answer is a List with embedded dictionaries of the form [{'id': 5, 'openat_cps_nummer': '123456'}, {...}]
        productpasses = self.read(cr, uid, ids, ['openat_csb_nummer'], context=context)
        print 'productpasses: %s' % productpasses

        # Only go on if product.product entries with a openat_csb_nummer where found
        if productpasses:
            # Get the object ir.model.data
            irmodeldata = self.pool.get('ir.model.data')

            # Browse through the found productpasses records: pprecord is a dict {'id': 5, 'openat_cps_nummer': '123456'}
            for pprecord in productpasses:
                print 'pprecord: %s ' % pprecord
                if pprecord['openat_csb_nummer']:

                    '''
                    # ToDo: Use correct Message template with all csv records to post message
                    print "Try to post a Message to the Record: %s" % pprecord['id']
                    template_obj = self.pool.get('email.template')
                    template_id = template_obj.search(cr, uid, [('name', '=', 'MikesTemplate')])[0]
                    print 'Email Template ID: %s' % template_id
                    template_obj.send_mail(cr, uid, template_id, pprecord['id'], force_send=False, context=context)
                    '''

                    # Alte Version ;)
                    #subject = 'Test Message at %s' % (lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    #self.message_post(cr, uid, pprecord['id'], body='Test', subject=subject)

                    # Search for the corresponding ir.model.data record. Answer is an id.
                    irmodeldata_record_id = irmodeldata.search(cr, uid, [('model', '=', 'product.product'),
                                                                         ('res_id', '=', pprecord['id'])])
                    print 'irmodeldata_record_id: %s' % irmodeldata_record_id
                    print 'len(irmodeldata_record_id): %s' % len(irmodeldata_record_id)
                    assert len(
                        irmodeldata_record_id) <= 1, 'More than one record found for ir.model.data: only one allowed'

                    # If a corresponding record already exists update the ir.model.data record with the csb number as name
                    if irmodeldata_record_id:
                        irmodeldata.write(cr, uid, irmodeldata_record_id,
                                          {'name': pprecord['openat_csb_nummer']},
                                          context=context)
                    # If none exists create a new one
                    # ToDo: Check the function export_data and see how it creates the external_id record
                    else:
                        irmodeldata.create(cr, uid,
                                           {'module': '__export__',
                                            'name': pprecord['openat_csb_nummer'],
                                            'model': 'product.product',
                                            'res_id': pprecord['id'], },
                                           context=None)

        print "--------------------------------------------------------"
        print "csbnummer_to_external_id(): STOP"
        print "--------------------------------------------------------"
        return True


    def button_tocheck(self, cr, uid, ids, context=None):
        self.check_valid_call(cr, uid, ids, context=context)
        return self.write(cr, uid, ids, {'state': 'pptocheck'}, context=context)

    def button_approved(self, cr, uid, ids, context=None):
        self.check_valid_call(cr, uid, ids, context=context)
        return self.write(cr, uid, ids,
                          {'state': 'ppapproved',
                           'approved_user': uid,
                           'approved_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
                          context=context)

    def button_nuts_approved(self, cr, uid, ids, context=None):
        self.check_valid_call(cr, uid, ids, context=context)
        return self.write(cr, uid, ids,
                          {'nuts_approved_user': uid,
                           'nuts_approved_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
                          context=context)

    def copy(self, cr, uid, ids, default=None, context=None):
        if default == None:
            default = {}
        default = default.copy()
        default.update({'openat_csb_nummer': False})
        default.update({'state': 'ppnew'})
        default.update({'openat_display': False})
        default.update({'openat_display_ids': False})
        print "copy(): default: %s" % default
        print "copy(): context: %s" % context
        return super(product_product, self).copy(cr, uid, ids, default, context=context)

    # Extend create, write and import_external (=load) functions
    # since these are NOT in the __init__ sections they will only be called on first save of a product.product
    # It may be necessary to move them into __init__ also?
    def create(self, cr, uid, vals, context=None):
        print "create(): Commands BEFORE original method is called"
        return super(product_product, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        print "write(): Commands BEFORE original method is called"
        self.csbnummer_to_external_id(cr, uid, ids, context=context)
        return super(product_product, self).write(cr, uid, ids, vals, context=context)

    def export_data(self, cr, uid, ids, fields_to_export, context=None):
        print "export_data(): Commands BEFORE original method is called"
        return super(product_product, self).export_data(cr, uid, ids, fields_to_export, context=context)

    def load(self, cr, uid, fields, data, context=None):
        print "--------------------------------------------------------"
        print "load(): Commands BEFORE original load method is called"
        print "--------------------------------------------------------"
        print "load() uid: %s" % uid
        print "load() fields: %s" % fields
        print "load() data: %s" % data
        print "load() context: %s" % context

        # TODO use export_data() to make a full backup of all products and post it as a message to a admin newsgroup

        # Add the ID field if not already present
        try:
            id_index = fields.index('id')
        except:
            # Add id to the end of fields list
            fields.append('id')
            # Add an empty string to the end of the tuples inside the data list
            data = [record + (u'',) for record in data]
            # prepare the index variable - this should also be available outside the try statement ?!?
            id_index = fields.index('id')
            print "load() fields after id field added: %s" % fields
            print "load() data after id field added: %s" % data

        # Make sure if there is a CSB-Nummer it is correctly used for the id field (external id)
        try:
            openat_csb_nummer_index = fields.index('openat_csb_nummer')
        except:
            print "load() no CSB Number found - But that's probably ok!"
        else:
            # Transfer the csb-nummer to the id field - don't change any other id field
            for x in range(0, len(data)):
                record = list(data[x])
                if record[openat_csb_nummer_index]:
                    record[id_index] = u'__export__.' + record[openat_csb_nummer_index]
                    data[x] = tuple(record)
                    print "load() data after csb number transfered: %s" % str(data)
                    print "load() record: %s" % record

        # Check if the state fields exists and if not add it and set the right state
        try:
            state_index = fields.index('state')
        except:
            print "load() no State field found - But that's probably ok!"
            # Add state field to the end of fields list
            fields.append('state')
            # Add an empty string to the end of the tuples inside the data list
            data = [record + (u'',) for record in data]
            # prepare the index variable.
            state_index = fields.index('state')
            print "load() fields after state field added: %s" % fields
            print "load() data after state field added: %s" % data
        # Add the correct state
        for x in range(0, len(data)):
            record = list(data[x])
            # Todo: Get all available Translation terms for product.template.state:ppapproved
            #source = self.pool.get('ir.translation')._get_source
            #print "load() self.pool.get('ir.translation')._get_source: %s" % source
            # End Todo
            if record[state_index] != u'ppapproved':
                try:
                    # If no CSB Number Field is present at all openat_csb_nummer_index will be undefined
                    # therefore we have to use try
                    if record[openat_csb_nummer_index]:
                        record[state_index] = u'pptocheck'
                except:
                    record[state_index] = u'ppnew'
            data[x] = tuple(record)

        print "load() data after state corrected: %s" % str(data)

        # Add the Import User name
        # ToDo find a way for the "First Import" user
        user = self.pool.get('res.users').browse(cr, uid, uid)
        print "load() user.name: %s " % user.name
        fields.append('user_update')
        data = [record + (unicode(user.name),) for record in data]

        # ToDo Check if a workflow is used instead of manually doing it - if the worklfow is also respected on import

        return super(product_product, self).load(cr, uid, fields, data, context=context)


product_product()


class partnerlines(osv.Model):
    _name = 'openat_produktpass.partnerlines'
    _columns = {
        'openat_produktpass_id': fields.many2one('product.product', 'Product Pass', required=True),
        'openat_partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'name': fields.char('Partner Article Name', translate=True),
    }

    def _check_unique(self, cr, uid, ids):
        print "_check_unique(self, cr, uid, ids): %s, %s, %s" % (cr, uid, ids)
        # Find if there are already partnerlines with this produktpass id
        for partnerline in self.browse(cr, uid, ids, context=None):
            print "_check_unique() partnerline.id: %s " % partnerline.id
            print "_check_unique() partnerline.openat_produktpass_id.id: %s " % partnerline.openat_produktpass_id.id
            print "_check_unique() partnerline.name: %s " % partnerline.name
            # If this combination of product.product and res.partner already exists its a missuse
            nonunique_ids = self.search(cr, uid,
                                        [('openat_produktpass_id', '=', partnerline.openat_produktpass_id.id,),
                                         ('openat_partner_id', '=', partnerline.openat_partner_id.id),
                                         ('id', '!=', partnerline.id),
                                        ])
            #(partnerline.openat_partner_id.id,'in','openat_partner_id')])
            print "_check_unique() Search results nonunique_ids: %s " % nonunique_ids
            if nonunique_ids:
                return False
        return True

    _constraints = [(_check_unique,
                     'Only one alternative Partner Article Name allowed! '
                     'Please to do not use the same PP and Partner combination twice',
                     ['openat_produktpass_id', 'openat_partner_id'])]


partnerlines()


class markenname(osv.Model):
    _name = 'openat_produktpass.markenname'
    _columns = {
        'name': fields.char('Brand Name', size=256, required=True, translate=False),
        'produktpass_ids': fields.many2many('product.product', string="Product Passes")
    }


markenname()


class lagerundtransport(osv.Model):
    _name = 'openat_produktpass.lagerundtransport'
    _columns = {
        'openat_produktpass_ids': fields.one2many('product.product', 'openat_lagerundtransport_id', 'Product Passes'),
        'name': fields.char('Name of Instruction', size=256, required=True, translate=False),
        'openat_temperatur': fields.integer('Temperature °C'),
        'openat_luftfeuchte': fields.integer('Humidity %'),
        'openat_licht': fields.text('Lighting Conditions'),
        'openat_lageranweisung': fields.text('Storage Instructions'),
        'openat_lieferanweisung': fields.text('Transport Instructions'),
        'openat_beschreibung': fields.text('Description'),
    }

lagerundtransport()


class konservierungsmethode(osv.Model):
    _name = 'openat_produktpass.konservierungsmethode'
    _columns = {
        'openat_produktpass_ids': fields.one2many('product.product', 'openat_konservierungsmethode_id', 'Product Passes'),
        'name': fields.char('Name of Preservation Method', size=256, required=True, translate=False),
        'openat_temp': fields.integer('Temperature °C'),
        'openat_zeit': fields.char('Time'),
        'openat_schutzbegasung': fields.char('Protective Gas'),
        'openat_gaszusammensetzung': fields.text('Gas Types'),
        'openat_beschreibung': fields.text('Description'),
    }

konservierungsmethode()


class kennzeichnung(osv.Model):
    _name = 'openat_produktpass.kennzeichnung'
    _columns = {
        'openat_produktpass_ids': fields.one2many('product.product', 'openat_kennzeichnung_id', 'Product Passes'),
        'name': fields.char('Name of Austrian Labeling', size=256, required=True, translate=True),
        'openat_beschreibung': fields.text('Description', required=True, translate=True)
    }

kennzeichnung()


class genusstauglichkeitskennzeichen(osv.Model):
    _name = 'openat_produktpass.genusstauglichkeitskennzeichen'
    _columns = {
        'openat_produktpass_ids': fields.one2many('product.product', 'openat_genusstauglichkeitskennzeichen_id', 'Product Pass'),
        'name': fields.char('Name', size=256, required=True, translate=False),
        'openat_gtk_number': fields.char('Number', translate=False),
        'openat_gtk_image': fields.binary('Image', filters='*.png,*.gif,*.jpg', translate=False)
    }

genusstauglichkeitskennzeichen()


class zertifikate(osv.Model):
    _name = 'openat_produktpass.zertifikate'
    _columns = {
        'name': fields.char('Name of Certificate', size=256, required=True, translate=True),
        'niveau': fields.char('Niveau - Grad', translate=False),
        'valid_until': fields.date('Valid Until'),
        'openat_produktpass_ids': fields.many2many('product.product', 'rel_produktpass_zertifikate',
                                                   'openat_zertifikat_id', 'openat_produktpass_id',
                                                   'Product Passes'),
    }

zertifikate()


class display(osv.Model):
    _name = 'openat_produktpass.display'
    _columns = {
        'produktpass_id': fields.many2one('product.product', 'Product Pass'),
        'name': fields.char('Art. Nr.', required=True, translate=True),
        'openat_bezeichnung': fields.text('Description', translate=True),
        'openat_eancode': fields.char('EAN-Code', translate=False),
        'openat_quantity': fields.char('Quantity', size=256, required=True, translate=True)
    }

display()

class mikrob(osv.Model):
    _name = 'openat_produktpass.mikrob'
    _columns = {
        'openat_produktpass_ids': fields.one2many('product.product', 'openat_mikrob_id', 'Product Passes'),
        'name': fields.char('Name', size=256, required=True, translate=True),
        # bei Ende MHD Richtwert
        'openat_mikrob_norm_keim': fields.char('Aer. mes. Gesamtkeimzahl (KBE / g)'),
        'openat_mikrob_norm_enterob': fields.char('Enterobacteriaceen (KBE / g)'),
        'openat_mikrob_norm_clost': fields.char('mes. sulfitred. Clostridien (KBE / g)'),
        'openat_mikrob_norm_coliforme': fields.char('Coliforme (KBE / g)'),
        'openat_mikrob_norm_coli': fields.char('E. Coli (KBE / g)'),
        'openat_mikrob_norm_entero': fields.char('Enterokokken (KBE / g)'),
        'openat_mikrob_norm_staphy': fields.char('koag. pos. Staphylokokken (KBE / g)'),
        'openat_mikrob_norm_lacto': fields.char('Lactobacillen (KBE / g)'),
        'openat_mikrob_norm_cerus': fields.char('Bacillus cereus (KBE / g)'),
        'openat_mikrob_norm_hefen': fields.char('Hefen (KBE / g)'),
        'openat_mikrob_norm_schimmel': fields.char('Schimmel (KBE / g)'),
        'openat_mikrob_norm_salmonellen': fields.char('Salmonellen (KBE / g)'),
        'openat_mikrob_norm_listeria': fields.char('Listeria monocytogenes (KBE / g)'),
        'openat_mikrob_norm_ehec': fields.char('EHEC (KBE / g)'),
        # bei Ende MHD Hoechstwert
        'openat_mikrob_max_keim': fields.char('Aer. mes. Gesamtkeimzahl (KBE / g)'),
        'openat_mikrob_max_enterob': fields.char('Enterobacteriaceen (KBE / g)'),
        'openat_mikrob_max_clost': fields.char('mes. sulfitred. Clostridien (KBE / g)'),
        'openat_mikrob_max_coliforme': fields.char('Coliforme (KBE / g)'),
        'openat_mikrob_max_coli': fields.char('E. Coli (KBE / g)'),
        'openat_mikrob_max_entero': fields.char('Enterokokken (KBE / g)'),
        'openat_mikrob_max_staphy': fields.char('koag. pos. Staphylokokken (KBE / g)'),
        'openat_mikrob_max_lacto': fields.char('Lactobacillen (KBE / g)'),
        'openat_mikrob_max_cerus': fields.char('Bacillus cereus (KBE / g)'),
        'openat_mikrob_max_hefen': fields.char('Hefen (KBE / g)'),
        'openat_mikrob_max_schimmel': fields.char('Schimmel (KBE / g)'),
        'openat_mikrob_max_salmonellen': fields.char('Salmonellen (KBE / g)'),
        'openat_mikrob_max_listeria': fields.char('Listeria monocytogenes (KBE / g)'),
        'openat_mikrob_max_ehec': fields.char('EHEC (KBE / g)'),
        #
    }

display()