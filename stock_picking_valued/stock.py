# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Pexego All Rights Reserved
#    $Jesús Ventosinos Mayor <jesus@pexego.es>$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api
from openerp.addons.decimal_precision import decimal_precision as dp


class stock_picking(models.Model):

    _inherit = "stock.picking"

    amount_untaxed = fields.Float(
        compute='_amount_all', digits=dp.get_precision('Sale Price'),
        string='Untaxed Amount', readonly=True, store=True)
    amount_tax = fields.Float(
        compute='_amount_all', digits=dp.get_precision('Sale Price'),
        string='Taxes', readonly=True, store=True)
    amount_total = fields.Float(
        compute='_amount_all', digits=dp.get_precision('Sale Price'),
        string='Total', readonly=True, store=True)
    amount_gross = fields.Float(
        compute='_amount_all', digits=dp.get_precision('Sale Price'),
        string='amount gross', readonly=True, store=True)
    amount_discounted = fields.Float(
        compute='_amount_all', digits=dp.get_precision('Sale Price'),
        string='Sale price', readonly=True, store=True)
    external_note = fields.Text(
        ' External Notes')

    @api.multi
    @api.depends('move_lines', 'partner_id',
                 'move_lines.purchase_line_id.price_unit',
                 'move_lines.purchase_line_id.discount',
                 'move_lines.procurement_id.sale_line_id.price_unit',
                 'move_lines.procurement_id.sale_line_id.discount',
                 'move_lines.product_uom_qty')
    def _amount_all(self):
        for picking in self:
            picking.amount_tax = picking.amount_untaxed = \
                picking.amount_gross = 0.0
            taxes = amount_gross = amount_untaxed = 0.0
            cur = picking.partner_id.property_product_pricelist \
                and picking.partner_id.property_product_pricelist.currency_id \
                or False
            for line in picking.move_lines:
                price_unit = 0.0
                if line.procurement_id and line.procurement_id.sale_line_id:
                    oline = line.procurement_id.sale_line_id
                    otaxes = oline.tax_id
                elif line.purchase_line_id:
                    oline = line.purchase_line_id
                    otaxes = oline.taxes_id
                else:
                    oline = False
                if oline and line.state != 'cancel':
                    price_unit = oline.price_unit * \
                        (1-(oline.discount or 0.0)/100.0)
                    for c in otaxes.compute_all(
                            price_unit, line.product_qty,
                            line.product_id,
                            oline.order_id.partner_id)['taxes']:
                        taxes += c.get('amount', 0.0)
                    amount_gross += (oline.price_unit *
                                     line.product_qty)
                    amount_untaxed += price_unit * line.product_qty
                else:
                    continue
            if cur:
                picking.amount_tax = cur.round(taxes)
                picking.amount_untaxed = cur.round(amount_untaxed)
                picking.amount_gross = cur.round(amount_gross)
            else:
                picking.amount_tax = round(taxes, 2)
                picking.amount_untaxed = round(amount_untaxed, 2)
                picking.amount_gross = round(amount_gross, 2)

            picking.amount_total = picking.amount_untaxed + picking.amount_tax
            picking.amount_discounted = picking.amount_gross - \
                picking.amount_untaxed


class stock_move(models.Model):

    _inherit = "stock.move"

    price_subtotal = fields.Float(
        compute='_get_subtotal', string="Subtotal",
        digits=dp.get_precision('Sale Price'), readonly=True,
        store=True)
    order_price_unit = fields.Float(
        compute='_get_subtotal', string="Price unit",
        digits=dp.get_precision('Sale Price'), readonly=True,
        store=True)
    cost_subtotal = fields.Float(
        compute='_get_subtotal', string="Cost subtotal",
        digits=dp.get_precision('Sale Price'), readonly=True,
        store=True)
    margin = fields.Float(
        compute='_get_subtotal', string="Margin",
        digits=dp.get_precision('Sale Price'), readonly=True,
        store=True)
    percent_margin = fields.Float(
        compute='_get_subtotal', string="% margin",
        digits=dp.get_precision('Sale Price'), readonly=True,
        store=True)

    @api.multi
    @api.depends('product_id', 'product_qty', 'procurement_id.sale_line_id',
                 'purchase_line_id', 'purchase_line_id.price_unit',
                 'purchase_line_id.discount',
                 'procurement_id.sale_line_id.price_unit',
                 'procurement_id.sale_line_id.discount')
    def _get_subtotal(self):
        for move in self:
            price_unit = 0
            if move.procurement_id.sale_line_id:
                price_unit = (move.procurement_id.sale_line_id.price_unit *
                              (1-(move.procurement_id.sale_line_id.discount or
                                  0.0)/100.0))
            elif move.purchase_line_id:
                price_unit = (move.purchase_line_id.price_unit *
                              (1-(move.purchase_line_id.discount or
                                  0.0)/100.0))
            cost_price = move.product_id.standard_price or 0.0
            move.price_subtotal = price_unit * move.product_qty
            move.order_price_unit = price_unit
            move.cost_subtotal = cost_price * move.product_qty
            move.margin = move.price_subtotal - move.cost_subtotal
            if move.price_subtotal > 0:
                move.percent_margin = (move.margin/move.price_subtotal)*100
            else:
                move.percent_margin = 0
