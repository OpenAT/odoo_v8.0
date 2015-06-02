# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 OpenERP s.a. (<http://openerp.com>).
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
    'name': "FRST Payment Provider",
    'summary': """Payment Provider: Bankeinzüge für FRST""",
    'description': """

Erlaubt es per Bankeinzug eine Dauerstpende oder Einmalspende zu tätigen
========================================================================

Dieses Addon erlaubt es per Bankeinzug eine Dauerstpende oder Einmalspende zu mit odoo durchzuführen. Es ist ein
neuer Payment Provider für odoo der auch das addon payment als Basis benutzt.

Bankeinzug (SEPA) Payment Provider für FRST
-------------------------------------------

- Neuer odoo PaymentProvider für SEPA Bankeinzug
- Front End JS to show IBAN und BIC Felder wenn dieser PP ausgewählt wird.
- Front End IBAN und BIC JS Überprüfung (website_tools jquery validate)
- Speichert IBAN und BIC direkt bei der payment.transactin
- Legt ein neues Bankkonto für res.partner an sollte es noch keines für diesen IBAN und BIC geben

ToDo:
- Backend IBAN und BIC Überprüfung und redirect zu payment wenn ein Fehler auftritt (derzeit error 500)

    """,
    'author': "DataDialog",
    'website': "http://www.datadialog.net/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'website_tools',
        'payment',
        'website_sale_payment_fix',
    ],
    'installable': True,
    'data': [
        # Template has to be loaded first because frst_data uses its id ;)
        'views/frst_acquirerbutton.xml',
        'data/frst_data.xml',
        'views/frst_transaction.xml',
    ],
}
