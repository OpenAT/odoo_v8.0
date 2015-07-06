# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import osv, fields
from openerp.addons.base_tools.image import resize_to_thumbnail

class BlogPost(osv.Model):
    _inherit = ['blog.post']

    def _get_square_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            # need to return also an dict for the image like result[1] = {'image_square': base_64_data}
            result[obj.id] = {'blogpost_image_square': False}
            if obj.blogpost_image:
                result[obj.id] = {'blogpost_image_square': resize_to_thumbnail(img=obj.blogpost_image, box=(180, 180),)}
        return result

    def _set_square_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'blogpost_image': value}, context=context)

    _columns = {
        'blogpost_image': fields.binary('Blog Post Image',),
        'blogpost_image_square': fields.function(_get_square_image, fnct_inv=_set_square_image,
            string="Blog Post Square Image (Auto crop and zoom)", type="binary", multi="_get_square_image",
            store=True),
    }
