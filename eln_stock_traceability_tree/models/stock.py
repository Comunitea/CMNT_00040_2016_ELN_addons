# -*- coding: utf-8 -*-
# Copyright 2022 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_default_uom = fields.Many2one(
        'product.uom', 'Unit of Measure',
        compute='_get_product_default_uom')

    @api.multi
    def _get_product_default_uom(self):
        for move in self:
            move.product_default_uom = move.product_id.uom_id
