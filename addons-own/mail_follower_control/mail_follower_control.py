# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 conexus (<http://conexus.at>).
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID


class res_partner(osv.Model):
    _inherit = "res.partner"

    _columns = {
        'no_subscribe': fields.boolean("Do not add as Follower automatically"),
    }
    
    _defaults = {
        'no_subscribe': True,
    }
    
    def get_partners_notify_by_email(self, cr, uid, ids, message_type, context):
        """ Return the list of partners which will be notified per mail, based on their preferences.
            :param message_type: type of message

        """
        notify_pids = []
        for partner in self.browse(cr, uid, ids):

            # Do not send to partners without email address defined
            if not partner.email:
                continue

            # Partner does not want to receive any emails
            if partner.notify_email == 'none':
                continue

            notify_pids.append(partner.id)

        return notify_pids
res_partner()

# Do not subscript followers with no_subscribe=True (except force_subscription is in the context)
# add data to mark follower in red that will not receive an email
class mail_thread(osv.AbstractModel):
    _inherit = "mail.thread"

    # overwrite full function to add 'notify_email': --> stupid but needed
    # (this function will be called by the java script mail_followers.js to get the follower data)
    # we need to know notify_email in the qweb template to mark followers in red that will not receive an email
    def read_followers_data(self, cr, uid, follower_ids, context=None):
        result = []
        technical_group = self.pool.get('ir.model.data').get_object(cr, uid, 'base', 'group_no_one', context=context)
        for follower in self.pool.get('res.partner').browse(cr, uid, follower_ids, context=context):
            is_editable = uid in map(lambda x: x.id, technical_group.users)
            is_uid = uid in map(lambda x: x.id, follower.user_ids)
            data = (follower.id,
                    follower.name,
                    {'is_editable': is_editable, 'is_uid': is_uid, 'notify_email': follower.notify_email, },
                    )
            result.append(data)
        return result

    # message_post will call message_subscribe to add followers
    # we alter this method to take our new field no_subscribe into account
    def message_subscribe(self, cr, uid, ids, partner_ids, subtype_ids=None, context=None):

        if context is None:
            context = {}

        # Update context: Filter all mail_post_autofollow_partner_ids if they exists to respect the no_subscribe setting
        # HINT: it seems that mail_post_autofollow_partner_ids could be different from partner_ids which seems weird?
        if context.get('mail_post_autofollow') and context.get('mail_post_autofollow_partner_ids'):
            context['mail_post_autofollow_partner_ids'] = self.pool.get('res.partner').search(cr, uid, [
                ('no_subscribe', '=', False),
                ('id', 'in', context.get('mail_post_autofollow_partner_ids'), )
            ])
        
        # Filter partner_ids: to respect the no_subscribe setting (except 'force_subscription' is set)
        # HINT: force_subscription is set by java script to allow adding a follower with no_subscribe=True by the
        #       add followers links in the chatter window - without this the follower could not be added by any method.
        if not context.get('force_subscription'):
            partner_ids = self.pool.get('res.partner').search(cr, uid, [
                ('no_subscribe', '=', False),
                ('id', 'in', partner_ids),
            ])

        res = super(mail_thread, self).message_subscribe(cr, uid, ids, partner_ids, subtype_ids, context)
        return res
mail_thread()


# Allow to add followers with the invite wizard
class invite_wizard(osv.osv_memory):
    _inherit = 'mail.wizard.invite'

    # Add force Subscription to the context so that followers can be added even if no_subscribe=True
    def add_followers(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context['force_subscription'] = True
        
        return super(invite_wizard, self).add_followers(cr, uid, ids, context)
invite_wizard()


class mail_compose_message(osv.TransientModel):
    _inherit = "mail.compose.message"
    
    _columns = {
        'follower_ids': fields.many2many('res.partner',
                                         'mail_compose_message_followers_rel',
                                         'wizard_id',
                                         'partner_id',
                                         string='Recipients (Followers)', readonly=True),
    }
    
    def get_record_data(self, cr, uid, values, context=None):
    
        res = super(mail_compose_message, self).get_record_data(cr, uid, values, context)
        
        if values.get('model') and values.get('res_id'):
            p_obj = self.pool.get('res.partner')
            fol_obj = self.pool.get("mail.followers")
            fol_ids = fol_obj.search(cr, SUPERUSER_ID, [
                    ('res_model', '=', values.get('model')),
                    ('res_id', '=', values.get('res_id')),
                    ('subtype_ids', 'in', 1)    # ID 1 is always the subtyp "Discussion"
                    ], context=context)
            followers = set(fo.partner_id for fo in fol_obj.browse(cr, SUPERUSER_ID, fol_ids, context=context))
            follower_ids = [f.id for f in followers]
            notify_pids = p_obj.get_partners_notify_by_email(cr, uid, follower_ids, 'comment', context)
            res.update({'follower_ids': notify_pids})

        return res

    def onchange_partner_ids(self, cr, uid, ids, partner_ids, context=None):
        
        p_ids = []        
        if isinstance(partner_ids, (list, tuple)):
            partner_ids = partner_ids[0]
        if isinstance(partner_ids, (list, tuple)) and partner_ids[0] == 4 and len(partner_ids) == 2:
            p_ids.add(partner_ids[1])
        if isinstance(partner_ids, (list, tuple)) and partner_ids[0] == 6 and len(partner_ids) == 3 and partner_ids[2]:
            p_ids = partner_ids[2]
        elif isinstance(partner_ids, (int, long)):
            p_ids.add(partner_ids)
        else:
            pass  # we do not manage anything else
        
        p_obj = self.pool.get('res.partner')        
        parterns_to_notify = p_obj.get_partners_notify_by_email(cr, uid, p_ids, "comment", context)
        
        partners_not_to_notify = [p for p in p_ids if p not in parterns_to_notify]        
        partners = p_obj.name_get(cr, uid, partners_not_to_notify, context=context)        
        partner_names = [p[1] for p in partners]                
        
        if partner_names:
            warning = {
                'title': _('Some partners will not be notified'),
                'message': _('The following partners will not be notified by e-mail because of their settings:\n\n%s') % ('\n'.join(partner_names))
            }
            res = {'warning': warning}
        else:
            res = {}
        return res
mail_compose_message()


class mail_message (osv.Model):
    _inherit = 'mail.message'

    def _message_read_dict(self, cr, uid, message, parent_id=False, context=None):
        res = super(mail_message, self)._message_read_dict(cr, uid, message, parent_id, context)
        
        # Search partner_ids from notifications
        if message:
            p_obj = self.pool.get('res.partner')
            cr.execute("""
                SELECT   n.partner_id
                FROM     mail_message m, mail_notification n
                WHERE    n.message_id = m.id
                AND      n.mail_sent is true                
                AND      m.id = %s""", (message.id,))            
            
            partner_ids = filter(None, map(lambda x: x[0], cr.fetchall()))
            partners = p_obj.name_get(cr, SUPERUSER_ID, partner_ids, context=context)  
            vals = {'notified_email_ids': partners}
            res.update(vals)
        
        return res


class mail_mail(osv.Model):
    _inherit = 'mail.mail'

    def send(self, cr, uid, ids, auto_commit=False, recipient_ids=None, context=None):
        if not context:
            context = {}
        context['email_partner_ids'] = recipient_ids
        res = super(mail_mail, self).send(cr, uid, ids, auto_commit, recipient_ids, context)
    
    def _postprocess_sent_message(self, cr, uid, mail, context=None, mail_sent=True):

        if mail_sent and context is not None:

            partner_ids = context.get('email_partner_ids', [])
            not_obj = self.pool.get('mail.notification')

            if partner_ids is not None and mail.mail_message_id:
                not_ids = not_obj.search(cr, SUPERUSER_ID, [
                    ('message_id', '=', mail.mail_message_id.id),
                    ('partner_id', 'in', partner_ids)
                ])

                not_obj.write(cr, SUPERUSER_ID, not_ids, {'mail_sent': True})

        return super(mail_mail, self)._postprocess_sent_message(cr=cr, uid=uid, mail=mail,
                                                                context=context, mail_sent=mail_sent)


class mail_notification(osv.Model):
    _inherit = 'mail.notification'
    
    _columns = {
        'mail_sent': fields.boolean('Sent Mail'),
    }