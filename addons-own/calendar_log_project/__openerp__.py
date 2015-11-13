# -*- coding: utf-8 -*-

{
    'name': "FCOM calendar_log_project",
    'summary': """Use the calender as a simple work log.""",
    'description': """
FCOM calendar_log_project
=========================

Use the calender as a simple work log.

    """,
    'author': "Data Dialog",
    'website': "http://www.datadialog.at",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'calendar',
        'project',
        'hr_timesheet_sheet',
        'project_timesheet',
        'calendar_log',
    ],
    'installable': True,
    'data': [
        'data/data.xml',
        'views/views.xml',
    ],
}
