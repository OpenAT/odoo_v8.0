# -*- coding: utf-8 -*-

##############################################################################

{
    'name': 'Openat Timetracking Setcharge',
    'version': '1.1',
    'author': 'Lightbase',
    'website': 'http://www.lightbase.com',
    'category': 'Project Management',
    'sequence': 8,
    'summary': 'Tasks, Issues',
    'depends': [
     'project_timesheet','project_issue_sheet',
    ],
    'data': [
        'project_task_view.xml',
        'project_issue_view.xml'
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
