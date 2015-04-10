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
    'name': "project_basic_extensions",
    'summary': """Basic Extension for Project, Tasks and Issues""",
    'description': """

Project, Task and Issues Extensions
===================================

- Sort order of grouped project kanaban view changed to sequence, id, name
- Add a Project description - etherpad enabled
- Show related Issues and Tasks as Lists in Project Form
- Show related Issues in Tasks as List and Smart Button in Form View
- Show related Tasks in Issues as List and Smart Button in Form View


    """,
    'author': "Michael Karrer michaelkarrer81@gmail.com",
    'website': "http://www.datadialog.net/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'base',
        'project',
        'pad',
        'project_issue',
    ],
    'installable': True,
    'data': [
        'views/views_project.xml',
        'views/views_task.xml',
    ],
}