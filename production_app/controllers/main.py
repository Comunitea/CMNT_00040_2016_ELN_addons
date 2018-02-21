# -*- coding: utf-8 -*-
import logging

from openerp import http

_logger = logging.getLogger(__name__)


class ProductionAppController(http.Controller):

    @http.route(['/productionApp/'], type='http', auth='public')
    def a(self, debug=False, **k):
        return http.local_redirect(
            '/production_app/static/productionApp/www/index.html')
