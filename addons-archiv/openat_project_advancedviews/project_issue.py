from openerp.osv import fields, osv

class openat_project_issue(osv.osv):
    _inherit = 'project.issue'
    
    def create(self, cr, uid, vals, context=None):
        context = context or {}
        res =  super(openat_project_issue, self).create(cr, uid, vals, context=context)
        issue = self.browse(cr, uid, res, context=context)

        if issue:
            if not issue.project_id:
                if issue.task_id:
                    if issue.task_id.project_id:
                        self.write(cr, uid, [res], {'project_id': issue.task_id.project_id.id}, context=context)
        return res

openat_project_issue()
