# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    show_in_app = fields.Boolean('Show in app',
                                 related='product_id.show_in_app')
