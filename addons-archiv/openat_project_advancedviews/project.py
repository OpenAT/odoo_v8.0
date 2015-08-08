from openerp.osv import fields, osv

class openat_project_project(osv.osv):
    _inherit = 'project.project'
    _columns = {
                'openat_issues': fields.one2many('project.issue', 'project_id', 'Issues'),
                }
    
openat_project_project()