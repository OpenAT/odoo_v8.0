# -*- coding: utf-8 -*-

{
    'name': "FCOM calendar_log",
    'summary': """Use the calender as a simple log. E.g. for meetings minutes or as a work log.""",
    'description': """
FCOM calendar_log
==================

Use the calender as a simple log. E.g. for meetings minutes or as a work log.

    """,
    'author': "Data Dialog",
    'website': "http://www.datadialog.at",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'base',
        'calendar',
        'crm',
        'calendar_category',
    ],
    'installable': True,
    'data': [
        'views/views.xml',
        'views/wizard.xml',
    ],
}
