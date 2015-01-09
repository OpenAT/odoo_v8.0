# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenAT
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

{
    'name': "OpenAT Produktpass",
    'version': "1.2",
    'category': "Tools",
    'summary': "openat_produktpass",
    'description': """
Dieses Addon erweiter product.product um eine Vielzahl neuer Felder die speziell fuer die Lebensmittelindusttrie
relevant sind. Diese neuen Felder sind in Reiter gegliedert und nur über spezielle Zugangsrechte sichtbar.

Die Produkte koennen entweder wie gewohnt in OpenERP angeleget werden oder aber über eine Schnittstelle zu CSB
importiert angelegt oder aktualisiert werde.

Einige Daten fuer Produkte die aus CSB importiert wurden können noch durch Informationen des Programmes NUTS ergaenzt
werden. Dies kann ebenfalls automatisch auf der Basis eines CSV-Exports von NUTS erledigt werden.
    """,
    'author': "OpenAT",
    'website': "http://www.OpenAT.at",
	'css' : ['static/src/css/style.css'],
    'images': [],
    'depends': ['base', 'product', 'product_expiry', 'stock', 'purchase', 'document', 'contacts'],
    'data': ['security/openat_produktpass_security.xml',
             'security/ir.model.access.csv',
             'view/openat_produktpass_view.xml',
             'view/openat_produktpass_markenname_view.xml',
             'view/openat_produktpass_lagerundtransport_view.xml',
             'view/openat_produktpass_konservierungsmethode_view.xml',
             'view/openat_produktpass_kennzeichnung_view.xml',
             'view/openat_produktpass_genusstauglichkeitskennzeichen_view.xml',
             'view/openat_produktpass_zertifikate_view.xml',
             'view/openat_produktpass_display_view.xml',
             'view/openat_produktpass_mikrob_view.xml',
             'view/openat_produktpass_menu.xml',
             'setup.xml'
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
