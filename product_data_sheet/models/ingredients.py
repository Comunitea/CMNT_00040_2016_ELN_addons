# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class ProductIngredient(models.Model):
    _name = 'product.ingredient'
    _order = 'product_qty desc'

    name = fields.Char('Name', size=256,
        required=True, translate=True)
    product_technical_sheet_id = fields.Many2one(
        'product.technical.sheet', 'Technical sheet',
        required=True, ondelete='cascade')
    product_id = fields.Many2one(
        'product.product', 'Product',
        required=True)
    product_qty = fields.Float('Product Qty',
        digits=dp.get_precision('Product Unit of Measure'),
        required=True)
    product_qty_percent = fields.Float('Qty(%)',
        digits=(16,3),
        compute='_get_product_qty_percent',
        readonly=True)
    origin = fields.Char('Origin', size=255, translate=True)
    caliber = fields.Char('Caliber', size=64, translate=True)
    process = fields.Char('Process', size=64, translate=True)
    variety = fields.Char('Variety', size=64, translate=True)

    @api.multi
    def _get_product_qty_percent(self):
        qty_total = sum(line.product_qty for line in self)
        if qty_total == 0.0:
            for line in self:
                line.product_qty_percent = 0.0
        else:
            qty_percent_acc = 0.0
            line_ids = self.sorted(key=lambda r: r.product_qty, reverse=True)
            for line in line_ids[1:]:
                qty_percent = round(((line.product_qty * 100) / qty_total), 3)
                qty_percent_acc += qty_percent
                line.product_qty_percent = qty_percent
            line_ids[0].product_qty_percent = 100 - qty_percent_acc

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name

