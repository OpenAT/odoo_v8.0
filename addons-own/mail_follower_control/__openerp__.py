# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Mail Follower Control',
    'version': '1.0',
    'category': 'Custom',
    'author': 'DataDialog (Michael Karrer), camadeus',
    'website': 'http://www.datadialog.net',
    'installable': True,
    'description': """
mail_follower_control
=====================

This addon allows better control over follower handling for the chatter view.

Goals:
------

- Checkbox "Do not automatically add as follower" for res.partner
- Set this new Checkbox to True by default
- Always show all the followers when sending an E-Mail AND allow to remove them
- CC and BCC Field for all Chatter E-Mails
    - Do NOT add BCC and CC Recipients as followers regardless of the checkbox "Do not automatically ad as follower"
- Show followers that will not receive Messages in Red
- Show followers that will seldom receive Messages in Orange
- Show a Warning when Sending an E-Mail if there are any Followers that will not receive the mail by config

    """,
    'depends': ['web', 'mail'],
    'qweb': [
        'views/templates.xml',
    ],
    'data': [
        'views/views.xml',
    ],

}