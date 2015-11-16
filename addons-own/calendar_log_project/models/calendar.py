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

        # Only start the timesheet-entry creation if the initial write has no errors
        if res:
            for event in self:

                # Check if this event is a worklog and has a related project or task
                if event.is_worklog and (event.task_id or event.project_id):

                    # Event has a related Task
                    if event.task_id:
                        # Create or update Task Work Log
                        values_worklog = {
                            'name': event.worklog_text or event.name,
                            'user_id': event.user_id.id,
                            'date': event.start_datetime,
                            'hours': event.duration,
                            'task_id': event.task_id.id,
                        }
                        # UNLINK hr.analytic.timesheet
                        if event.analytic_time_id:
                            event.analytic_time_id.unlink()

                        # CREATE (No Worklog exists)
                        if not event.task_work_id:
                            event.task_work_id = event.task_id.work_ids.create(values_worklog)
                        # UPDATE (Worklog exists - relinks to new task if changed)
                        else:
                            event.task_work_id.write(values_worklog)

                    # Event has no related task but a related project
                    elif event.project_id:
                        # Get the Values for hr.analytic.timesheet
                        time_obj = self.env['hr.analytic.timesheet']
                        values_hr_line = {
                            'name': event.worklog_text or event.name,
                            'user_id': event.user_id.id,
                            'date': event.start_datetime,
                            'unit_amount': event.duration,
                            'account_id': event.project_id.analytic_account_id.id,
                            'journal_id': time_obj._getAnalyticJournal(context={'user_id': event.user_id.id}),
                            'product_id': time_obj._getEmployeeProduct(context={'user_id': event.user_id.id}),
                            'product_uom_id': time_obj._getEmployeeUnit(context={'user_id': event.user_id.id}),
                            'general_account_id': time_obj._getGeneralAccount(context={'user_id': event.user_id.id}),
                        }
                        # Recheck the UOM and recalculate if needed
                        default_uom = event.env['res.users'].browse(event.user_id.id).company_id.project_time_mode_id.id
                        if values_hr_line['product_uom_id'] != default_uom:
                            values_hr_line['unit_amount'] = self.pool['product.uom']._compute_qty(default_uom, values_hr_line['unit_amount'], values_hr_line['product_uom_id'])

                        if event.task_work_id:
                            # Unlink task worklog
                            event.task_work_id.unlink()

                        if not event.analytic_time_id:
                            # Create analytic timeline entry
                            event.analytic_time_id = event.analytic_time_id.create(values_hr_line)
                        else:
                            # Update analytic timeline entry
                            event.analytic_time_id.write(values_hr_line)

                # If this event is not a worklog delete all related task and timesheet entries if any
                else:
                    if event.task_work_id:
                        event.task_work_id.unlink()
                    if event.analytic_time_id:
                        event.analytic_time_id.unlink()

        return res
