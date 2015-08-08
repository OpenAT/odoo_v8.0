from openerp.osv import fields, osv

class openat_project_task(osv.Model):
    
    _inherit = 'project.task'
    
    def openat_issue_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0)        
        issue_ids = self.pool.get('project.issue').search(cr, uid, [('task_id', 'in', ids)])
        for issue in self.pool.get('project.issue').browse(cr, uid, issue_ids, context):
            res[issue.task_id.id] = 0
            if issue.state not in ('done', 'cancelled'):
                res[issue.task_id.id] += 1
        return res
    
    _columns = {
      'openat_issue_count': fields.function(openat_issue_count, type='integer', string="Unclosed Issues"),
      'openat_issues': fields.one2many('project.issue', 'task_id', 'Issues'),
      }
    
openat_project_task()    