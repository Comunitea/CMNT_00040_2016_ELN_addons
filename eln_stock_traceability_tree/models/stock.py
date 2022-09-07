# -*- coding: utf-8 -*-
# Copyright 2022 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_default_uom = fields.Many2one(
        'product.uom', 'Unit of Measure',
        related='product_id.uom_id',
        readonly=True)
