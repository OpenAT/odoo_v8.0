# -*- coding: utf-8 -*-
##############################################################################
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

from openerp import models
from openerp import SUPERUSER_ID

class ir_mail_server(models.Model):
    _inherit = "ir.mail_server"

    def send_email(self, cr, uid, message, mail_server_id=None, smtp_server=None, smtp_port=None,
                   smtp_user=None, smtp_password=None, smtp_encryption=None, smtp_debug=False,
                   context=None):
        # Add a global bcc email address to all messages send by odoo if defined in mail.outgoing.global.bcc
        # Usefull to store a copy of every E-Mail from odoo on own mail server
        global_bcc = self.pool['ir.config_parameter'].get_param(cr, SUPERUSER_ID,
                                                                'mail.outgoing.global.bcc',
                                                                default=None, context=context)
        if global_bcc != 'NoMail' and message.get('To', None):
            if message.get('Bcc', None):
                message['Bcc'] += ', ' + global_bcc
            else:
                message['Bcc'] = global_bcc

        return super(ir_mail_server, self).send_email(cr, uid, message, mail_server_id, smtp_server, smtp_port,
                                                      smtp_user, smtp_password, smtp_encryption, smtp_debug,
                                                      context)

