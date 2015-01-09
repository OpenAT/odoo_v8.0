__author__ = 'mkarrer'

def _send_invoice(self, cr, uid, ids, context=None):
        """ Send invoice to customer using a specified email template """

        if context is None:
            context = {}

        templ_obj = self.pool.get('email.template')
        m_obj  = self.pool.get('ir.model.data')
        att_obj = self.pool.get('ir.attachment')

        context['default_model'] = 'account.invoice'
        context['mark_invoice_as_sent'] = True

        old_uid = uid
        for invoice in self.pool.get('account.invoice').browse(cr, uid, ids):
            # Set current user to Sales Person (E-Mail FROM)
            if invoice.user_id:
                 uid = invoice.user_id.id
            else:
                uid = old_uid

            # If the template_id in the workflow is not set: do not send an email
            if not invoice.workflow_id.invoice_template_id:
                continue

            comp_ctx = dict(context, active_ids=[invoice.id])
            # Render template and use the following values: body, subject, attachment, model, res_id
            composer_values = templ_obj.generate_email(cr, uid, invoice.workflow_id.invoice_template_id.id, invoice.id, context=None)

            # Create PDF
            attachment_ids = []
            for attachment in composer_values.get('attachments', []):
                attachment_data = {
                    'name': attachment[0],
                    'datas_fname': attachment[0],
                    'datas': attachment[1],
                    'res_model': 'account.invoice',
                    'res_id': invoice.id,
                    'partner_id': invoice.partner_id.id,
                }
                attachment_ids.append(att_obj.create(cr, uid, attachment_data, context=context))

            # Create a new e-mail (mail.message)
            # partner_ids will be added as follower
            values = {
                'partner_ids': [(6,0,[invoice.partner_id.id])],
                'attachment_ids': [(6,0,attachment_ids)],
                'body': composer_values.get('body'),
                'subject': composer_values.get('subject'),
                'model': composer_values.get('model', False),
                'res_id': composer_values.get('res_id', False),
            }

            # Create a wizard object (same as in frontend when mail is sent manually)
            composer_id = self.pool['mail.compose.message'].create(cr, uid, values, context=comp_ctx)
            # Send mail (and attach to chatter history)
            self.pool['mail.compose.message'].send_mail(cr, uid, [composer_id], context=comp_ctx)
        uid = old_uid
        return True