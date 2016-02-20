# -*- coding: utf-8 -*-

from openerp import tools, api
from openerp.fields import Many2one, Boolean, Char, Float, Date, One2many
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID

class calendar_event_category(osv.osv):
    _inherit = 'calendar.event.category'

    is_worklog = Boolean(string='Is Worklog',
                         help='Default Is Worklog setting for meetings with this category',
                         default=False)

class hr_analytic_timesheet(osv.osv):
    _inherit = 'hr.analytic.timesheet'
    event_category_id = Many2one('calendar.event.category', string='Event Category', readonly=False)


class calendar_event(osv.osv):
    _inherit = 'calendar.event'

    is_worklog = Boolean(string='Is Worklog', help='Create a Work-Log Entry', default=False)
    project_id = Many2one('project.project', string='Project')
    task_id = Many2one('project.task', string='Task')
    worklog_text = Char('Work-Log', size=128)
    task_work_id = Many2one('project.task.work', string='Task Worklog ID')
    analytic_time_id = Many2one('hr.analytic.timesheet', string='HR Analytic Timesheet ID')

    # DISABLED FOR NOW Update the field event_category_id at installation or update
    # def init(self, cr, context=None):
    #     print "INIT OF calendar_log_project"
    #     events = self.browse(cr, SUPERUSER_ID, self.search(cr, SUPERUSER_ID, []))
    #     for event in events:
    #         # We trigger the write method at install or update time for all events to update the event_category_id
    #         event.write({"name": event.name or None})

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
        # Unlink any existing task_work_id if task has changed
        # So we force a task_work_id create which will create a new task_work_id.hr_analytic_timesheet_id!
        if 'task_id' in values and self.task_work_id and self.ensure_one():
            self.task_work_id.hr_analytic_timesheet_id.unlink()
            self.task_work_id.unlink()

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

                    # Update the related hr.analytic.timesheet of the task_work_id with event_category_id
                    self.task_work_id.hr_analytic_timesheet_id.write({'event_category_id': self.category_id.id, })

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
                        'event_category_id': self.category_id.id,
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

    @api.multi
    def unlink(self):
        for event in self:
            if event.task_work_id:
                event.task_work_id.unlink()
            if event.analytic_time_id:
                event.analytic_time_id.unlink()
        return super(calendar_event, self).unlink()


class hr_timesheet_sheet_sheet_day_cat_detail(osv.osv):
    _name = "hr_timesheet_sheet.sheet.day_cat_detail"
    _description = "Category by Days in Period"
    _auto = False
    _order = 'name'

    # Fields:
    name = Date(string='Date', readonly='True')
    timesheet_id = Many2one(comodel_name='hr_timesheet_sheet.sheet', string='Timesheet')
    employee_id = Many2one(comodel_name='hr.employee', string='Employee')

    ga = Float(string="GA", readonly='True')
    ga_e = Float(string="GA Expense", readonly='True')
    ga_a = Float(string="GA Abroad", readonly='True')
    ga_ae = Float(string="GA Abroad Expense", readonly='True')

    cm = Float(string="CM", readonly='True')
    cm_e = Float(string="CM Expense", readonly='True')
    cm_a = Float(string="CM Abroad", readonly='True')
    cm_ae = Float(string="CM Abroad Expense", readonly='True')

    t = Float(string="T", readonly='True')
    t_e = Float(string="T Expense", readonly='True')
    t_a = Float(string="T Abroad", readonly='True')
    t_ae = Float(string="T Abroad Expense", readonly='True')

    os = Float(string="OS", readonly='True')
    os_e = Float(string="OS Expense", readonly='True')
    os_a = Float(string="OS Abroad", readonly='True')
    os_ae = Float(string="OS Abroad Expense", readonly='True')

    sum_e = Float(string="Expense", readonly='True')
    sum_a = Float(string="Abroad", readonly='True')
    sum_ae = Float(string="Abroad Expense", readonly='True')

    # Sum of the events categories per day
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'hr_timesheet_sheet_sheet_day_cat_detail')
        cr.execute(""" CREATE OR REPLACE VIEW hr_timesheet_sheet_sheet_day_cat_detail as (
            select
                 ts.id * 100000 + ((period.day::date - ts.date_from::timestamp::date) + 1) AS id
                ,ts.id timesheet_id
                ,ts.employee_id
                ,ts.user_id
                ,period.day as name
                ,count(distinct e.id)
                ,sum(case when cc.name = 'GENERAL ACTIVITY' then e.duration else 0 end) ga
                ,sum(case when cc.name = 'GENERAL ACTIVITY > Expense Entitled' then e.duration else 0 end) ga_e
                ,sum(case when cc.name = 'GENERAL ACTIVITY > Abroad' then e.duration else 0 end) ga_a
                ,sum(case when cc.name = 'GENERAL ACTIVITY > Abroad > Expense Entitled' then e.duration else 0 end) ga_ae
                ,sum(case when cc.name = 'CUSTOMER MEETING' then e.duration else 0 end) cm
                ,sum(case when cc.name = 'CUSTOMER MEETING > Expense Entitled' then e.duration else 0 end) cm_e
                ,sum(case when cc.name = 'CUSTOMER MEETING > Abroad' then e.duration else 0 end) cm_a
                ,sum(case when cc.name = 'CUSTOMER MEETING > Abroad > Expense Entitled' then e.duration else 0 end) cm_ae
                ,sum(case when cc.name = 'TRIP' then e.duration else 0 end) t
                ,sum(case when cc.name = 'TRIP > Expense Entitled' then e.duration else 0 end) t_e
                ,sum(case when cc.name = 'TRIP > Abroad' then e.duration else 0 end) t_a
                ,sum(case when cc.name = 'TRIP > Abroad > Expense Entitled' then e.duration else 0 end) t_ae
                ,sum(case when cc.name = 'OVERNIGHT STAY > Expense Entitled' then e.duration else 0 end) os_e
                ,sum(case when cc.name = 'OVERNIGHT STAY > Abroad' then e.duration else 0 end) os_a
                ,sum(case when cc.name = 'OVERNIGHT STAY > Abroad > Expense Entitled' then e.duration else 0 end) os_ae
                ,sum(case when cc.name = 'OVERNIGHT STAY' then e.duration else 0 end) os
                -- ,sum(case when cc.name like '%Expense%' then e.duration else 0 end) sum_exp
                -- ,sum(case when cc.name like '%Abroad%' then e.duration else 0 end) sum_abr
                ,sum(case when cc.name in ( 'GENERAL ACTIVITY > Expense Entitled'
                                           ,'CUSTOMER MEETING > Expense Entitled'
                                           ,'TRIP > Expense Entitled'
                                            ) then e.duration else 0 end) sum_e
                ,sum(case when cc.name in ( 'GENERAL ACTIVITY > Abroad'
                                           ,'CUSTOMER MEETING > Abroad'
                                           ,'TRIP > Abroad'
                                            ) then e.duration else 0 end) sum_a
                ,sum(case when cc.name in ( 'GENERAL ACTIVITY > Abroad > Expense Entitled'
                                           ,'CUSTOMER MEETING > Abroad > Expense Entitled'
                                           ,'TRIP > Abroad > Expense Entitled'
                                            ) then e.duration else 0 end) sum_ae
                ,p.name partner_name
            from   hr_timesheet_sheet_sheet ts
            inner join res_users u
                on u.id = ts.user_id
            inner join res_partner p
                on p.id = u.partner_id
            cross join generate_series(ts.date_from::timestamp without time zone, ts.date_to::timestamp without time zone, '1 day'::interval) period(day)
            left join calendar_event e
                on e.user_id = ts.user_id
                   and e.start_datetime::timestamp::date = period.day::timestamp::date
                   and e.category_id in (select id from calendar_event_category where name in
                                                        ('GENERAL ACTIVITY'
                                                        ,'GENERAL ACTIVITY > Expense Entitled'
                                                        ,'GENERAL ACTIVITY > Abroad'
                                                        ,'GENERAL ACTIVITY > Abroad > Expense Entitled'
                                                        ,'CUSTOMER MEETING'
                                                        ,'CUSTOMER MEETING > Expense Entitled'
                                                        ,'CUSTOMER MEETING > Abroad'
                                                        ,'CUSTOMER MEETING > Abroad > Expense Entitled'
                                                        ,'TRIP'
                                                        ,'TRIP > Expense Entitled'
                                                        ,'TRIP > Abroad'
                                                        ,'TRIP > Abroad > Expense Entitled'
                                                        ,'OVERNIGHT STAY > Expense Entitled'
                                                        ,'OVERNIGHT STAY > Abroad'
                                                        ,'OVERNIGHT STAY > Abroad > Expense Entitled'
                                                        ,'OVERNIGHT STAY'))

            left join calendar_event_category cc
                on cc.id = e.category_id
            group by
                 ts.id
                ,ts.employee_id
                ,ts.user_id
                ,period.day
                ,p.name
            order by ts.id, period.day
            )""")


class hr_timesheet_sheet(osv.osv):
    _inherit = 'hr_timesheet_sheet.sheet'

    day_cat_details = One2many(comodel_name='hr_timesheet_sheet.sheet.day_cat_detail',
                               inverse_name='timesheet_id',
                               string='Day Cat Details',
                               readonly='True')

