# -*- coding: utf-8 -*-

import datetime
import werkzeug
import logging
_logger = logging.getLogger(__name__)

from openerp import SUPERUSER_ID
from openerp.tools.translate import _

from openerp import http
from openerp.http import request
from openerp.addons.website.models.website import slug
from openerp.addons.web.controllers.main import login_redirect
from openerp.tools import html2plaintext


# Import an other controller for extension
from openerp.addons.website_sale.controllers.main import website_sale

# Use the odoo logger
_logger = logging.getLogger(__name__)


class website_sale_extended(website_sale):
    _logger.info('Controller website_sale was extended!')
