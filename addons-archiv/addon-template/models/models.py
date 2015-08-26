# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)

from openerp import models, fields, api
from openerp import SUPERUSER_ID
from openerp.tools.translate import _


# Camle Case for Classes
class ExampleModel(models.Model):
    # Lower Case for _name
    _name = 'example.model'

    # New API Field Creation
    name = fields.Char()
