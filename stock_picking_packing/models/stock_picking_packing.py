# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields
import openerp.addons.decimal_precision as dp


class StockPickingPacking(models.Model):
    _name = 'stock.picking.packing'
    _order = 'product_pack, product_id, lot_id'

    picking_id = fields.Many2one(
        'stock.picking', 'Stock Picking',
        required=True,
        ondelete="cascade",
        help='The stock operation where the packing has been made')
    product_id = fields.Many2one(
        'product.product', 'Product')
    product_qty = fields.Float(
        'Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        required=True)
    product_uom_id = fields.Many2one(
        'product.uom', 'Unit of Measure',
        required=True)
    product_qty_uos = fields.Float('Quantity (UOS)',
        digits=dp.get_precision('Product UoS'))
    product_uos_id = fields.Many2one(
        'product.uom', 'Product UOS')
    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial Number')
    pack_ul_id = fields.Many2one(
        'product.ul', 'Package Logistic Unit',
        required=True)
    product_pack = fields.Integer('Pack N.')

