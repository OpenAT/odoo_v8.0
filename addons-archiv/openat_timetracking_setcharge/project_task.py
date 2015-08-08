from openerp.osv import fields, osv

class openat_project_task_work(osv.osv):
    _inherit = "project.task.work"
    
    def create(self, cr, uid, vals, context=None):
        context = context or {}
        to_invoice_id = False
        res =  super(openat_project_task_work, self).create(cr, uid, vals, context=context)
        work = self.browse(cr, uid, res, context=context)        
                                
        if work.hr_analytic_timesheet_id:
                if work.hr_analytic_timesheet_id.line_id:
                    if work.openat_invoiceable:
                        to_invoice_id = work.openat_invoiceable.id            
                    else:
                        if work.task_id.project_id:
                            if work.task_id.project_id.analytic_account_id:
                                if work.task_id.project_id.analytic_account_id.to_invoice:
                                    to_invoice_id = work.task_id.project_id.analytic_account_id.to_invoice.id
                    acc_ana_line = self.pool.get('account.analytic.line')
                    acc_ana_line.write(cr, uid, [work.hr_analytic_timesheet_id.line_id.id], {'to_invoice': to_invoice_id}, context=context)
        
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        context = context or {}
        acc_ana_line = self.pool.get('account.analytic.line')
        res = super(openat_project_task_work, self).write(cr, uid, ids, vals, context=context)
        if res:
            for work in self.browse(cr, uid, ids, context=context):
                if work.hr_analytic_timesheet_id:
                    if work.hr_analytic_timesheet_id.line_id:
                        if work.openat_invoiceable.id != work.hr_analytic_timesheet_id.line_id.to_invoice.id:
                            if work.openat_invoiceable:
                                acc_ana_line.write(cr, uid, [work.hr_analytic_timesheet_id.line_id.id], {'to_invoice': work.openat_invoiceable.id}, context=context)
                            else:
                                to_invoice_id = False
                                if work.task_id.project_id:
                                    if work.task_id.project_id.analytic_account_id:
                                        if work.task_id.project_id.analytic_account_id.to_invoice:
                                            to_invoice_id = work.task_id.project_id.analytic_account_id.to_invoice.id
                                acc_ana_line.write(cr, uid, [work.hr_analytic_timesheet_id.line_id.id], {'to_invoice': to_invoice_id}, context=context)
        return res
    
    _columns = {
                'openat_invoiceable': fields.many2one('hr_timesheet_invoice.factor', 'Invoiceable'),
                }
    
openat_project_task_work()


class openat_hr_analytic_timesheet(osv.osv):
    _inherit = "hr.analytic.timesheet"
    
    def create(self, cr, uid, vals, context=None):
        context = context or {}
        res =  super(openat_hr_analytic_timesheet, self).create(cr, uid, vals, context=context)
        ts = self.browse(cr, uid, res, context=context)
        if ts.line_id:
            to_invoice_id = False
            if ts.openat_invoiceable:
                to_invoice_id = ts.openat_invoiceable.id
            else:
                if ts.issue_id:
                    if ts.issue_id.project_id:
                        if ts.issue_id.project_id.analytic_account_id:
                            if ts.issue_id.project_id.analytic_account_id.to_invoice:
                                to_invoice_id = ts.issue_id.project_id.analytic_account_id.to_invoice.id
            acc_ana_line = self.pool.get('account.analytic.line')
            acc_ana_line.write(cr, uid, [ts.line_id.id], {'to_invoice': to_invoice_id}, context=context)
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        context = context or {}
        acc_ana_line = self.pool.get('account.analytic.line')
        res = super(openat_hr_analytic_timesheet, self).write(cr, uid, ids, vals, context=context)
        if res:
            for ts in self.browse(cr, uid, ids, context=context):
                if ts.line_id:
                    if ts.openat_invoiceable:
                        if ts.openat_invoiceable.id != ts.line_id.to_invoice.id:
                            acc_ana_line.write(cr, uid, [ts.line_id.id], {'to_invoice': ts.openat_invoiceable.id}, context=context)
                    else:
                        to_invoice_id = False
                        if ts.issue_id:
                            if ts.issue_id.project_id:
                                if ts.issue_id.project_id.analytic_account_id:
                                    if ts.issue_id.project_id.analytic_account_id.to_invoice:
                                        to_invoice_id = ts.issue_id.project_id.analytic_account_id.to_invoice.id
                        acc_ana_line.write(cr, uid, [ts.line_id.id], {'to_invoice': to_invoice_id}, context=context)
        return res
    
    _columns = {
                'openat_invoiceable': fields.many2one('hr_timesheet_invoice.factor', 'Invoiceable'),
                }
    
openat_hr_analytic_timesheet()
