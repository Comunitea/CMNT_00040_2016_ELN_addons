# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved.
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sample_ok = fields.Boolean('Sample?', default=False)

    @api.onchange('sample_ok')
    def onchange_sample_ok(self):
        """
            Sets sale line price unit to zero if 'sample_ok' field is check
        """
        if self.product_id:
            if self.sample_ok:
                price_unit = 0.0
            else:
                pricelist_id = self._context.get('pricelist', False)
                partner_id = self._context.get('partner_id', False)
                date_order = self._context.get('date_order', False)
                fiscal_position = self._context.get('fiscal_position', False)
                res = super(SaleOrderLine, self).product_id_change(
                    pricelist_id, self.product_id.id,
                    self.product_uom_qty, self.product_uom.id,
                    self.product_uos_qty, self.product_uos.id,
                    self.name, partner_id, False, True,
                    date_order, self.product_packaging.id,
                    fiscal_position, False)
                res = res.get('value', {})
                price_unit =  res.get('price_unit') or False
            self.price_unit = price_unit


class SaleOrder(models.Model):
    _inherit = 'sale.order'

   
    def action_ship_create(self):
        """
            Extend this method for updating stock move based on sale_order_line 'sample' field...
        """
        res = super(SaleOrder, self).action_ship_create()
        for order in self:
            sample_line_ids = order.order_line.filtered(lambda r: r.sample_ok)
            samples_location = order.warehouse_id.samples_loc_id.id
            if sample_line_ids and samples_location:
                move_ids = order.picking_ids.mapped('move_lines')
                moves_to_upgrade = move_ids.filtered(lambda r: r.procurement_id.sale_line_id in sample_line_ids)
                moves_to_upgrade.write({'location_id': samples_location})
        return res

