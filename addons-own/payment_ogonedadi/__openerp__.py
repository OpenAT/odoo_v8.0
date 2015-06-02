# -*- coding: utf-8 -*-

{
    'name': 'Ogone Payment Acquirer extended by Datadialog',
    'category': 'Hidden',
    'summary': 'Payment Acquirer: Ogone Implementation extended by Datadialog',
    'version': '1.1',
    'description': """Ogone Payment Provider extended by Datadialog""",
    'author': 'OpenERP SA and DataDialog, Michael Karrer (michael.karrer@datadialog.net)',
    'depends': [
        'payment',
        'website_sale_payment_fix'],
    'data': [
        'views/ogonedadi.xml',
        'views/payment_acquirer.xml',
        'views/templates_ogone_checkout.xml',
        'data/ogonedadi.xml',
    ],
    'installable': True,
}
