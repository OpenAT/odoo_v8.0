# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp.osv import fields, orm

# Add a sequence and a fold field
class account_analytic_account(orm.Model):
    _name = 'account.analytic.account'
    _inherit = ['account.analytic.account']
    _columns = {
        'fold': fields.boolean('Folded in Kanban Views'),
        'sequence': fields.integer('Sequence', select=True, help="Custom Order Sequence for Analytic Accounts."),
    }
    _defaults = {
        'sequence': 10,
    }


class project(orm.Model):
    _name = "project.project"
    _inherit = ["project.project", 'pad.common']

    def _read_group_parent_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        # HINT: You do NOT get the IDS of the current model (project.project in this case)
        #       but the ids for the model of the grouped_by many2one field (eg.: parent_id of account.analytic.account)!
        analytic_obj = self.pool.get('account.analytic.account')
        access_rights_uid = access_rights_uid or uid
        order = self._order

        # This removes duplicates and sorts the ids by order
        search_domain = []
        search_domain += [('id', 'in', ids)]
        analytic_ids = analytic_obj._search(cr, access_rights_uid, search_domain, order=order, access_rights_uid=access_rights_uid, context=context)

        # get a list of tuples with account_id and display_name
        result = analytic_obj.name_get(cr, access_rights_uid, analytic_ids, context=context)

        # Restore the Order of the tuples? Todo find out why!
        result.sort(lambda x, y: cmp(analytic_ids.index(x[0]), analytic_ids.index(y[0])))

        fold = {}
        for account in analytic_obj.browse(cr, uid, analytic_ids, context=context):
            fold[account.id] = account.fold or False

        return result, fold

    _group_by_full = {
        'parent_id': _read_group_parent_ids
    }

    _columns = {
        'description': fields.text('Project Description'),
        'description_pad': fields.char('Project Description PAD', pad_content_field='description'),
        # Override the original sequence field of project.project
        'sequence': fields.related('analytic_account_id', 'sequence',
                                   type='integer', string='Sequence', store=True),
    }

    _order = "sequence"