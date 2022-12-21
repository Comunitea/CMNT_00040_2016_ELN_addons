# -*- coding: utf-8 -*-
import logging

from openerp import http

_logger = logging.getLogger(__name__)


class WarehouseAppController(http.Controller):

    @http.route(['/warehouseApp/'], type='http', auth='public')
    def a(self, debug=False, **k):
        return http.local_redirect(
            '/warehouse_app/static/warehouseApp/www/index.html')
