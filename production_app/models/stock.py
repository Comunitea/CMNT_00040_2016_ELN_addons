# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    reason_id = fields.Many2one('scrap.reason', 'Reason')
