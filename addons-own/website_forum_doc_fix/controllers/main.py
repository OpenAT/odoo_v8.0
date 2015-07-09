# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request

# import the base controller class to inherit from
from openerp.addons.website_forum_doc.controllers.main import WebsiteDoc

# Inherit from WebsiteDoc
class WebsiteDocFix(WebsiteDoc):
    @http.route()
    # Full overwrite of the post_doc_ok method
    def post_toc_ok(self, forum, post_id, toc_id, **kwargs):
        cr, uid, context = request.cr, request.uid, request.context
        user = request.registry['res.users'].browse(cr, uid, uid, context=context)
        assert user.karma >= 200, 'Not enough karma, you need 200 to promote a documentation.'

        post_obj = request.registry['forum.post']
        doc_stage_id = False
        post = post_obj.browse(cr, uid, [int(post_id)])
        if post.documentation_stage_id:
            doc_stage_id = post.documentation_stage_id.id
        else:
            documentation_stage_obj = request.registry['forum.documentation.stage']
            doc_stage_id = documentation_stage_obj.search(cr, uid, [], limit=1, context=context)[0]

        post_obj.write(cr, uid, [int(post_id)], {
            'documentation_toc_id': toc_id and int(toc_id) or False,
            'documentation_stage_id': doc_stage_id,
        }, context=context)
        return request.redirect('/forum/'+str(forum.id)+'/question/'+str(post_id))
