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
from openerp import _, api, fields, models
import openerp.addons.decimal_precision as dp


class MrpModifyConsumptionLine(models.TransientModel):

    _name = 'mrp.modify.consumption.line'
    _order = 'product_id'

    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_qty = fields.Float(
        'Quantity (in default UoM)',
        digits=dp.get_precision('Product Unit of Measure'))
    lot_id = fields.Many2one('stock.production.lot', 'Lot')
    uom_id = fields.Many2one('product.uom', 'Unit of measure', required=True)
    location_id = fields.Many2one('stock.location', 'Source location',
                                  required=True)
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
            self.move_id = self.move_id.copy(
                {'product_uom_qty': self.product_qty,
                 'restrict_lot_id': self.lot_id.id,
                 'product_uom': self.uom_id.id,
                 'location_id': self.location_id.id})
        else:
            production = self.env['mrp.production'].browse(
                self._context.get('active_id', False))
            self.move_id = self.env['stock.move'].create(
                {'name': production.name,
                 'date': production.date_planned,
                 'date_expected': production.date_planned,
                 'product_id': self.product_id.id,
                 'product_uom_qty': self.product_qty,
                 'product_uom': self.uom_id.id,
                 'location_id': self.location_id.id,
                 'location_dest_id': production.location_dest_id.id,
                 'company_id': production.company_id.id,
                 'raw_material_production_id': production.id,
                 'price_unit': self.product_id.standard_price,
                 'origin': production.name,
                 'procure_method': 'make_to_stock',
                 'warehouse_id':
                    self.env['stock.location'].get_warehouse(self.location_id),
                 'group_id': production.move_prod_id.group_id.id,
                 'restrict_lot_id': self.lot_id.id
                 })
        self.move_id.action_confirm()

    @api.multi
    def modify_move(self):
        self.ensure_one()
        self.move_id.write({'restrict_lot_id': self.lot_id.id,
                            'product_uom_qty': self.product_qty,
                            'product_uom': self.uom_id.id,
                            'location_id': self.location_id.id})


    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id

class MrpModifyConsumption(models.TransientModel):

    _name = 'mrp.modify.consumption'

    line_ids = fields.One2many('mrp.modify.consumption.line', 'wiz_id',
                               'Lines')

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
                quant_qty = self.env['product.uom']._compute_qty_obj(
                    quant.product_id.uom_id, quant.qty, move.product_uom)
                qty = quant_qty < total and quant_qty or total
                try:
                    exist_line = (x for x in lines
                                  if x['lot_id'] == quant.lot_id.id and
                                  x['location_id'] == quant.location_id.id and
                                  x['move_id'] == move.id).next()
                    exist_line['product_qty'] += qty
                except StopIteration:
                    lines.append({'product_id': quant.product_id.id,
                                  'product_qty': qty,
                                  'lot_id': quant.lot_id.id,
                                  'uom_id': move.product_uom.id,
                                  'location_id': quant.location_id.id,
                                  'move_id': move.id})
                total -= qty
            if total > 0:
                lines.append({'product_id': move.product_id.id,
                              'location_id': move.location_id.id,
                              'product_qty': total,
                              'lot_id': False,
                              'uom_id': move.product_uom.id,
                              'move_id': move.id})
        res.update(line_ids=lines)
        return res

    @api.multi
    def modify(self):
        self.mapped('line_ids.move_id').do_unreserve()
        modified_moves = []
        for line in self.line_ids.filtered(lambda r: r.product_qty > 0.0):
            if not line.move_id or line.move_id.id in modified_moves:
                line.create_move()
            else:
                line.modify_move()
                modified_moves.append(line.move_id.id)
        self.mapped('line_ids.move_id').action_assign()
        return {'type': 'ir.actions.act_window_close'}
