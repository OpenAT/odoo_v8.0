# -*- coding: utf-8 -*-

{
    'name': "FCOM calendar_log",
    'summary': """Use the calender as a simple log""",
    'description': """

This is the Header
==================

Some description text what this addon is all about.

Maybe a subheader
-----------------

And some more information

    """,
    'author': "Data Dialog",
    'website': "http://www.datadialog.at",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'base',
        'calendar',
        'crm',
    ],
    'installable': True,
    'css': [
        #'static/src/css/chatter.css',
        #'static/src/css/backend.css',
        ],
    'data': [
        # DATA
        #'data/data.xml',
        # SECURITY FILES
        #'security/ir.model.access.csv',
        #'security/ir_ui_view.xml',
        # VIEWS AND TEMPLATES
        #'views/res_config.xml',
        #'views/ir_actions.xml',
        #'views/templates.xml',
        #'views/snippets.xml',
        'views/views.xml',
    ],
    'js': [
        #'static/src/js/default.js',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'data/demo.xml',
    ],
}