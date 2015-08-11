# -*- coding: utf-8 -*-

{
    'name': "FCOM calendar_category",
    'summary': """calendar categories""",
    'description': """
FCOM calendar_category
======================

calendar categories

    """,
    'author': "Data Dialog",
    'website': "http://www.datadialog.at",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'calendar',
    ],
    'installable': True,
    'data': [
        'data/data.xml',
        'views/views.xml',
        'security/ir.model.access.csv',
    ],
}
