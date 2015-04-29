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


class mail_thread(osv.AbstractModel):
    _inherit = "mail.thread"

    # Add data for JS to mark follower in red that will not receive an email
    #
    # FULL OVERWRITE of function to add 'notify_email': --> stupid but needed
    # (this function will be called by the java script mail_followers.js to get the follower data)
    # we need to know notify_email in the qweb template to mark followers in red that will not receive an email
    # we alter mail_followers.js in addons-own/mail_follower_control/static/src/js/mail_follower_control.js to add
    # notify_email to the display_followers function
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

    # Do not subscript followers with no_subscribe=True (except force_subscription is in the context)
    #
    # message_post will call message_subscribe to add followers
    # we alter this method to take our new field no_subscribe into account
    def message_subscribe(self, cr, uid, ids, partner_ids, subtype_ids=None, context=None):
        if context is None:
            context = {}

        # Update context: Filter all mail_post_autofollow_partner_ids if they exists to respect the no_subscribe setting
        # Todo: Ask Andi why mail_post_autofollow_partner_ids could be different from partner_ids which seems weird?
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


# Allow to add followers with no_subscribe=True at least with the invite wizard (Add Followers Link)
class invite_wizard(osv.osv_memory):
    _inherit = 'mail.wizard.invite'

    # Add force Subscription to the context so that followers can be added even if no_subscribe=True
    def add_followers(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context['force_subscription'] = True
        
        return super(invite_wizard, self).add_followers(cr, uid, ids, context)
invite_wizard()


class mail_message(osv.Model):
    _inherit = "mail.message"
    # Add field recipient_ids to store this data from mail.mail if a mail was sent
    _columns = {
        'recipient_ids': fields.many2many('res.partner', string='Partners notified by e-mail'),
    }

    # Update Dict for JS rendering of messages with field recipient_ids
    # HINT: _message_read_dict returns a dict representation of the message. This representation is
    #       used in the JS client code, to display the messages. Partners and
    #       attachments related stuff will be done in post-processing in batch.
    def _message_read_dict(self, cr, uid, message, parent_id=False, context=None):
        res = super(mail_message, self)._message_read_dict(cr, uid, message, parent_id, context)

        # ToDo: Create a dict wich holds name and id for each id in ids (partner) - needed in template!
        vals = {'recipient_ids': [[p.id, p.name] for p in message.recipient_ids]}
        # print 'vals: %s' % vals
        res.update(vals)
        return res

mail_message()


# Check Receipients while composing a mail (Full compsoing dialog not quick dialogue) and give a warning
# if the added recipients will not receive an e-mail by setting
class mail_compose_message(osv.TransientModel):
    _inherit = "mail.compose.message"

    _columns = {
        'follower_ids': fields.many2many('res.partner',
                                         'mail_compose_message_followers_rel',
                                         'wizard_id',
                                         'partner_id',
                                         string='Notified by eMail', readonly=True),
    }

    # This will recalculate/set the field follower_ids for the current mail_compose_message (which is a transient model
    # so its not a problem to recalculate it here on the fly)
    def get_record_data(self, cr, uid, values, context=None):

        res = super(mail_compose_message, self).get_record_data(cr, uid, values, context)

        # if this message belongs to a resource add follower ids that will receieve an email to the result dict
        if values.get('model') and values.get('res_id'):
            p_obj = self.pool.get('res.partner')
            fol_obj = self.pool.get("mail.followers")

            # get all followers for the current resource (= model and res_id)
            fol_ids = fol_obj.search(cr, SUPERUSER_ID, [
                    ('res_model', '=', values.get('model')),
                    ('res_id', '=', values.get('res_id')),
                    ('subtype_ids', 'in', 1)    # ID 1 is always the subtyp "Discussion"
                    ], context=context)

            # get the res.partner objects of the followers (mail.followers) of this resource
            followers = set(fo.partner_id for fo in fol_obj.browse(cr, SUPERUSER_ID, fol_ids, context=context))

            # get the res.partner ids for the objects in followers
            follower_ids = [f.id for f in followers]

            # filter out all followers without an email or with notify_email set to none
            notify_pids = p_obj.get_partners_notify_by_email(cr, uid, follower_ids, 'comment', context)

            # add follower_ids tp the result dict
            # This result dict is used by the ??? - I DONT KNOW TILL NOW!
            res.update({'follower_ids': notify_pids})

        return res

    def onchange_partner_ids(self, cr, uid, ids, partner_ids, follower_ids, model, res_id, context=None):

        # We unwrap the variable partner_ids which most likely has a form of e.g. [(6, 0, [7]), ]
        # see https://doc.odoo.com/v6.0/developer/2_5_Objects_Fields_Methods/methods.html/#osv.osv.osv.write
        p_ids = []
        # Unwrap: Only take the first list or tuble
        if isinstance(partner_ids, (list, tuple)):
            partner_ids = partner_ids[0]
        # 4 means "link to existing record with id = ID" so we add new links which in fact is nonsense since
        # p_ids is empty at this time anyway.
        if isinstance(partner_ids, (list, tuple)) and partner_ids[0] == 4 and len(partner_ids) == 2:
            p_ids.add(partner_ids[1])
        # 6 means "replace the list of linked IDs" so we replace the partner ids
        if isinstance(partner_ids, (list, tuple)) and partner_ids[0] == 6 and len(partner_ids) == 3 and partner_ids[2]:
            p_ids = partner_ids[2]
        elif isinstance(partner_ids, (int, long)):
            p_ids.add(partner_ids)
        else:
            pass  # we do not manage anything else
        
        p_obj = self.pool.get('res.partner')

        # get all partners that have an email and also notify_email is not none
        parterns_to_notify = p_obj.get_partners_notify_by_email(cr, uid, p_ids, "comment", context)

        # find any partners in p_ids that are not in parterns_to_notify
        partners_not_to_notify = [p for p in p_ids if p not in parterns_to_notify]

        # get the names of the partners that will not get an email
        partners = p_obj.name_get(cr, uid, partners_not_to_notify, context=context)        
        partner_names = [p[1] for p in partners]

        # Update follower_ids
        # Update the values for the wizzard (found in addons/email_template/wizard/mail_compose_message.py)
        # HINT: There was no docu in how to update the wizard but at least i found an example - i have no idea
        #       If this is the same for all wizards
        f_ids = []
        # Unwrap: Only take the first list or tuble
        if isinstance(follower_ids, (list, tuple)):
            follower_ids = follower_ids[0]
        # 4 means "link to existing record with id = ID" so we add new links which in fact is nonsense since
        # f_ids is empty at this time anyway.
        if isinstance(follower_ids, (list, tuple)) and follower_ids[0] == 4 and len(follower_ids) == 2:
            f_ids.add(follower_ids[1])
        # 6 means "replace the list of linked IDs" so we replace the follower ids
        if isinstance(follower_ids, (list, tuple)) and follower_ids[0] == 6 and len(follower_ids) == 3 and follower_ids[2]:
            f_ids = follower_ids[2]
        elif isinstance(follower_ids, (int, long)):
            f_ids.add(follower_ids)
        else:
            pass  # we do not manage anything else

        # update the follower_ids to reflect the newly added partners to notify by mail if any
        values = {'follower_ids': list(set(f_ids + parterns_to_notify)), }


        # warn if any partners found that will not get an email
        if partner_names:
            warning = {
                'title': _('Some partners will not be notified by e-mail!'),
                'message': _('The following partners will not be notified by e-mail but they will still get a message in odoo (if they are have a login):\n\n%s') % ('\n'.join(partner_names))
            }
            res = {'warning': warning, 'value': values}
        else:
            res = {'value': values}
        return res
mail_compose_message()




# This will update the new custom field mail_sent for the model mail.notification - seems useless ... because
# it will be true if the smtp server takes over the mail which des not guarantee sending was successful
class mail_mail(osv.Model):
    _inherit = 'mail.mail'

    def _postprocess_sent_message(self, cr, uid, mail, context=None, mail_sent=True):

        # Copy the recipient_ids to the mail.message
        # Hint: It seems this is not necessary because at this stage recipient_ids of mail.message is already
        #       the same than recipient_ids of mail.mail ?!? thgouth it would be different for inherit**s**
        #       ToDo: Have to ask andi about this!!!
        #if mail_sent and mail.recipient_ids and mail.mail_message_id:
            #mail.mail_message_id.recipient_ids = mail.recipient_ids

        return super(mail_mail, self)._postprocess_sent_message(cr=cr, uid=uid, mail=mail,
                                                                context=context, mail_sent=mail_sent)


# class mail_notification(osv.Model):
#     _inherit = 'mail.notification'
#     _columns = {
#         'mail_sent': fields.boolean('Sent Mail'),
#     }