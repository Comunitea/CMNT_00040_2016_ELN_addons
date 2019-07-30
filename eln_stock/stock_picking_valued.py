# -*- coding: utf-8 -*-
# Copyright 2019 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class StockMove(models.Model):
    _inherit = 'stock.move'

    price_subtotal = fields.Float(
        compute='_get_move_subtotal', string="Subtotal",
        digits=dp.get_precision('Account'), readonly=True,
        store=True)
    order_price_unit = fields.Float(
        compute='_get_move_subtotal', string="Price unit",
        digits=dp.get_precision('Product Price'), readonly=True,
        store=True)
    cost_subtotal = fields.Float(
        compute='_get_move_subtotal', string="Cost subtotal",
        digits=dp.get_precision('Account'), readonly=True,
        store=True)
    margin = fields.Float(
        compute='_get_move_subtotal', string="Margin",
        digits=dp.get_precision('Account'), readonly=True,
        store=True)
    percent_margin = fields.Float(
        compute='_get_move_subtotal', string="% margin",
        digits=dp.get_precision('Account'), readonly=True,
        store=True)

    @api.multi
    @api.depends('product_id', 'product_uom_qty', 'date')
    def _get_move_subtotal(self):
        for move in self:
            price_unit = 0.0
            if move.procurement_id.sale_line_id:
                price_unit = (move.procurement_id.sale_line_id.price_unit * (1-(move.procurement_id.sale_line_id.discount or 0.0)/100.0))
            elif move.purchase_line_id:
                price_unit = (move.purchase_line_id.price_unit * (1-(move.purchase_line_id.discount or 0.0)/100.0))
            else:
                price_unit = 0.0
            cost_price = self.env['product.template'].get_history_price(
                move.product_id.product_tmpl_id.id, move.company_id.id, date=move.date)
            cost_price = cost_price or move.with_context(force_company=move.company_id.id).product_id.standard_price
            move.price_subtotal = price_unit * move.product_uom_qty
            move.order_price_unit = price_unit
            move.cost_subtotal = cost_price * move.product_uom_qty
            move.margin = move.price_subtotal - move.cost_subtotal
            if move.price_subtotal > 0:
                move.percent_margin = (move.margin/move.price_subtotal)*100
            else:
                move.percent_margin = 0

