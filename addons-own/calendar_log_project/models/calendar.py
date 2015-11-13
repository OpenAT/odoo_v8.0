# -*- coding: utf-8 -*-

from openerp import tools, api
from openerp.fields import Many2one, Boolean, Char, Text
from openerp.osv import fields, osv

class calendar_event_category(osv.osv):
    _inherit = 'calendar.event.category'

    is_worklog = Boolean(string='Is Worklog',
                         help='Default Is Worklog setting for meetings with this category',
                         default=False)


class calendar_event(osv.osv):
    _inherit = 'calendar.event'

    is_worklog = Boolean(string='Is Worklog', help='Create a Work-Log Entry', default=False)
    project_id = Many2one('project.project', string='Project')
    task_id = Many2one('project.task', string='Task')
    worklog_text = Char('Work-Log', size=128)
    task_work_id = Many2one('project.task.work', string='Task Worklog ID')
    analytic_time_id = Many2one('hr.analytic.timesheet', string='HR Analytic Timesheet ID')

    @api.onchange('category_id')
    def _set_worklog(self):
        if self.category_id:
            self.is_worklog = self.category_id.is_worklog

    @api.onchange('task_id')
    def _set_project(self):
        if self.task_id:
            # Set the Project to the project_id of the Task
            if self.project_id != self.task_id.project_id:
                self.project_id = self.task_id.project_id
            # Set the Main Partner to the task or project partner
            if not self.mainpartner_id:
                if self.task_id.partner_id:
                    self.mainpartner_id = self.task_id.partner_id
                elif self.project_id.partner_id:
                    self.mainpartner_id = self.project_id.partner_id

    @api.onchange('project_id')
    def _set_task(self):
        # https://github.com/odoo/odoo/issues/4574
        if self.project_id:
            # Clear the Task if it has a different project_id
            if self.task_id:
                if self.task_id.project_id != self.project_id:
                    self.task_id = False

            # Try to set the Main Partner
            if not self.mainpartner_id:
                if self.task_id and self.task_id.partner_id:
                    self.mainpartner_id = self.task_id.partner_id
                elif self.project_id.partner_id:
                    self.mainpartner_id = self.project_id.partner_id

            # Set a domain for the task list to only show tasks that belong to this project
            return {'domain': {'task_id': [('project_id', '=', self.project_id.id)]}}
        else:
            # Clear the Domain for Tasks if no Project is selected
            return {'domain': {'task_id': []}}

    @api.multi
    def write(self, values):
        res = super(calendar_event, self).write(values)

        if res and self.ensure_one():
            # Create or Update related hr.analytic.timesheet entries
            if self.is_worklog and (self.task_id or self.project_id):
                if self.task_id:
                    # Create or update Task Work Log
                    values_worklog = {
                        'name': self.worklog_text or self.name,
                        'user_id': self.user_id.id,
                        'date': self.start_datetime,
                        'hours': self.duration,
                        'task_id': self.task_id.id,
                    }
                    # UNLINK hr.analytic.timesheet
                    if self.analytic_time_id:
                        self.analytic_time_id.unlink()

                    # CREATE (No Worklog exists)
                    if not self.task_work_id:
                        self.task_work_id = self.task_id.work_ids.create(values_worklog)
                    # UPDATE (Worklog exists - relinks to new task if changed)
                    else:
                        self.task_work_id.write(values_worklog)
                elif self.project_id:
                    # Get the Values for hr.analytic.timesheet
                    time_obj = self.env['hr.analytic.timesheet']
                    values_hr_line = {
                        'name': self.worklog_text or self.name,
                        'user_id': self.user_id.id,
                        'date': self.start_datetime,
                        'unit_amount': self.duration,
                        'account_id': self.project_id.analytic_account_id.id,
                        'journal_id': time_obj._getAnalyticJournal(context={'user_id': self.user_id.id}),
                        'product_id': time_obj._getEmployeeProduct(context={'user_id': self.user_id.id}),
                        'product_uom_id': time_obj._getEmployeeUnit(context={'user_id': self.user_id.id}),
                        'general_account_id': time_obj._getGeneralAccount(context={'user_id': self.user_id.id}),
                    }
                    # Recheck the UOM and recalculate if needed
                    default_uom = self.env['res.users'].browse(self.user_id.id).company_id.project_time_mode_id.id
                    if values_hr_line['product_uom_id'] != default_uom:
                        values_hr_line['unit_amount'] = self.pool['product.uom']._compute_qty(default_uom, values_hr_line['unit_amount'], values_hr_line['product_uom_id'])

                    if self.task_work_id:
                        # Unlink task worklog
                        self.task_work_id.unlink()

                    if not self.analytic_time_id:
                        # Create analytic timeline entry
                        self.analytic_time_id = self.analytic_time_id.create(values_hr_line)
                    else:
                        # Update analytic timeline entry
                        self.analytic_time_id.write(values_hr_line)
            else:
                # UNLINK Work Logs
                if self.task_work_id:
                    self.task_work_id.unlink()
                if self.analytic_time_id:
                    self.analytic_time_id.unlink()

        return res
