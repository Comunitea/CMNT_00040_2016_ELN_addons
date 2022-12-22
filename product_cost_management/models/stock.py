# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def get_price_from_cost_structure(self):
        for move in self:
            if move.production_id and move.product_id.cost_structure_id:
                ctx = self._context.copy()
                ctx.update(
                    product_id=move.product_id.id,
                    bom_id=move.production_id.bom_id.id,
                )
                pcl_obj = self.env['product.costs.line']
                cost = pcl_obj.with_context(ctx).get_product_costs()
                price = cost.get('inventory_cost', False)
                if price:
                    move.write({'price_unit': price})

    @api.multi
    def quant_price_update_after_produce(self):
        self.get_price_from_cost_structure()
        for move in self:
            quant_ids = move.mapped('quant_ids')
            quant_ids.sudo().write({'cost': move.price_unit})

    @api.multi
    def product_price_update_after_produce(self):
        """ Copy function of product_price_update_before_done with productions
            locations
        """
        tmpl_dict = {}
        for move in self:
            # Adapt standard price on production moves if
            # the product cost_method is 'average'
            if (move.location_id.usage == 'production') and \
                    (move.product_id.cost_method == 'average'):
                product = move.product_id
                prod_tmpl_id = move.product_id.product_tmpl_id.id
                qty_available = move.product_id.product_tmpl_id.qty_available
                # Because move is done and we don't want the move qty yet
                qty_available -= move.product_qty
                if qty_available <= 0:
                    qty_available = 0.0
                if tmpl_dict.get(prod_tmpl_id):
                    product_avail = qty_available + tmpl_dict[prod_tmpl_id]
                else:
                    tmpl_dict[prod_tmpl_id] = 0
                    product_avail = qty_available
                if product_avail <= 0:
                    new_std_price = move.price_unit
                else:
                    # Get the standard price
                    amount_unit = product.standard_price
                    new_std_price = ((amount_unit * product_avail) +
                                     (move.price_unit * move.product_qty)) / \
                                     (product_avail + move.product_qty)
                tmpl_dict[prod_tmpl_id] -= move.product_qty
                # Write the standard price, as SUPERUSER_ID because a warehouse manager
                # may not have the right to write on products
                ctx = self._context.copy()
                ctx.update(
                    force_company=move.company_id.id,
                )
                values = {'standard_price': new_std_price}
                product.sudo().with_context(ctx).write(values)

    @api.multi
    def action_done(self):
        res = super(StockMove, self).action_done()
        move_ids = self.filtered(
            lambda r: r.state == 'done' and not r.scrapped and r.production_id)
        move_ids.quant_price_update_after_produce()
        move_ids.product_price_update_after_produce()
        return res


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    cost = fields.Float('Unit Cost', digits=dp.get_precision('Product Price'))


class StockHistory(models.Model):
    """
    Added to reload stock_history view, because is deleted when we put the
    precision to the stock quant cost field
    """
    _inherit = 'stock.history'

    def init(self, cr):
        super(StockHistory, self).init(cr)
