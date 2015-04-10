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

    # Add a default sort order to the kanban view
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

        # Restore the Order of the tuples?
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

# Add new fields to tasks to be able to display a smart button for issue
class task(orm.Model):
    _name = 'project.task'
    _inherit = ['project.task']

    def _issue_count(self, cr, uid, ids, field_name, arg, context=None):
        issue_obj = self.pool.get('project.issue')
        # We use a dict comprehension to generate a dict in the form of {task_id: count, ...}
        # HINT: Issues in a Stage with fold=True are not counted - this is the default of odoo!
        return {task_id: issue_obj.search_count(cr, uid, [('task_id', '=', task_id), ('stage_id.fold', '=', False)], context=context)
                for task_id in ids
                }

    _columns = {
        # this field gets a list from the function which seems not right for me - expected to be just an int
        # odoo must have some sort of auto handling for this - maybe this is for graph view widgets in the button
        # and not plain numbers http://de.slideshare.net/openobject/odoo-smart-buttons
        'issue_count': fields.function(_issue_count, type='integer', string='Issues'),

        # Since we already have a many2one field in project.issue this field is just the inverse of it
        # which will be automatically filled with the issue ids related to this task
        # It is still unclear to me why this field has to exist?!? doesnt seem to be related to the button.
        'issue_ids': fields.one2many('project.issue', 'task_id',)
    }

    def action_open_related_project_form(self, cr, uid, ids, context=None):
        project_id = self.pool.get('project.project').search(cr, uid, [('task_ids', 'in', ids)])
        if len(project_id) == 1:
            context.update({'active_id': project_id[0], })
            res_id = project_id[0]
        return {
            'name': _('Project'),
            'res_model': 'project.project',
            'type': 'ir.actions.act_window',
            'views': [[False, "form"]],
            'context': context,
            'res_id': res_id or None,
            # this could open the project in edit mode -
            # be careful you have to also set a default view or there will be no edit buttons
            #'target': 'inline',
        }

    def action_open_issue_kanban(self, cr, uid, ids, context=None):
        task = self.browse(cr, uid, ids, context=context)[0]
        context.update({
            'search_default_task_id': task.id,
            'default_task_id': task.id,
            'default_project_id': task.project_id.id,
            'default_partner_id': task.partner_id.id,
            })
        return {
            'name': _('Issue'),
            'res_model': 'project.issue',
            'type': 'ir.actions.act_window',
            'views': [[False, "kanban"], [False, "tree"], [False, "form"], [False, "calendar"], [False, "graph"]],
            'context': context,
        }
