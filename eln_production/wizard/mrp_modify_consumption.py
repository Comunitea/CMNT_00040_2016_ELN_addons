# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Comunitea All Rights Reserved
#    $Jesús Ventosinos Mayor <jesus@comunitea.com>$
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
from openerp import _, api, exceptions, fields, models
import openerp.addons.decimal_precision as dp


class MrpModifyConsumptionLine(models.TransientModel):

    _name = 'mrp.modify.consumption.line'

    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_qty = fields.Float(
        'Quantity (in default UoM)',
        digits=dp.get_precision('Product Unit of Measure'))
    lot_id = fields.Many2one('stock.production.lot', 'Lot')
    location_id = fields.Many2one('stock.location', 'Source location')
    move_id = fields.Many2one('stock.move', 'Move')
    wiz_id = fields.Many2one('mrp.modify.consumption', 'Wizard')

    @api.multi
    def split(self):
        self.ensure_one()
        self.copy({'product_qty': 0})
        return self.wiz_id.wizard_view()

    @api.multi
    def create_move(self):
        self.ensure_one()
        if self.move_id:
            self.move_id = self.move_id.copy({'restrict_lot_id': self.lot_id.id,
                                              'product_uom_qty': self.product_qty,
                                              'location_id': self.location_id.id})
            self.move_id.action_confirm()
        else:
            if self.product_id.type != 'service':
                production = self.wiz_id.production_id
                self.move_id = production._make_consume_line_from_data(self.wiz_id.production_id, self.product_id, self.product_id.uom_id.id, self.product_qty, False, 0)
                if self.location_id and self.location_id != self.move_id.location_id:
                    self.move_id.write({'location_id': self.location_id.id})
                self.move_id.action_confirm()

    @api.multi
    def modify_move(self):
        self.ensure_one()
        self.move_id.write({'restrict_lot_id': self.lot_id.id,
                            'product_uom_qty': self.product_qty,
                            'location_id': self.location_id.id})


class MrpModifyConsumption(models.TransientModel):

    _name = 'mrp.modify.consumption'

    production_id = fields.Many2one('mrp.production', 'Production')
    line_ids = fields.One2many('mrp.modify.consumption.line', 'wiz_id', 'Lines')

    @api.multi
    def wizard_view(self):
        view = self.env.ref('eln_production.mrp_modify_consumption_form')
        return {
            'name': _('Modify consumptions'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mrp.modify.consumption',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': self.env.context,
        }

    @api.model
    def default_get(self, fields):
        res = super(MrpModifyConsumption, self).default_get(fields)
        production_id = self._context.get('active_id', False)
        production = self.env['mrp.production'].browse(production_id)
        lines = []
        for move in production.move_lines:
            total = move.product_uom_qty
            for quant in move.reserved_quant_ids:
                qty = quant.qty < total and quant.qty or total
                lines.append({'product_id': quant.product_id.id,
                              'product_qty': qty, 'lot_id': quant.lot_id.id,
                              'location_id': quant.location_id.id,
                              'move_id': move.id})
                total -= qty
            if total > 0:
                lines.append({'product_id': move.product_id.id,
                              'product_qty': total, 
                              'location_id': move.location_id.id,
                              'move_id': move.id})
        res.update(line_ids=lines, production_id=production_id)
        return res

    @api.multi
    def modify(self):
        self.mapped('line_ids.move_id').do_unreserve()
        modified_moves = []
        for line in self.line_ids.filtered(lambda r: r.product_qty > 0.0):
            if line.move_id.id in modified_moves or not line.move_id:
                line.create_move()
            else:
                line.modify_move()
                modified_moves.append(line.move_id.id)
        self.mapped('line_ids.move_id').action_assign()
        to_remove_ids = self.mapped('production_id.move_lines') - self.mapped('line_ids.move_id')
        if to_remove_ids:
            to_remove_ids.action_cancel()
            to_remove_ids.unlink()
        return {'type': 'ir.actions.act_window_close'}
