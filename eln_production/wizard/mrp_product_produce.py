# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Javier Colmenero Fern´andez$ <javier@comunitea.com>
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
from openerp import models, fields, api, exceptions, _


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    mode = fields.Selection(selection_add=[('produce', 'Solo fabricar')])

    @api.multi
    def on_change_qty(self, product_qty, consume_lines):
        """
            Get the products to consume when product is already confirmed
            Se llama a super aunque luego se sobreescriben los consumos para
            calcularlos correctamente.
        """
        context = self._context
        if context.get('active_id') and context.get('default_mode', False) and \
                context['default_mode'] == 'consume':
            production = self.env['mrp.production'].browse(context['active_id'])
            if production.move_created_ids2:
                product_qty = production.move_created_ids2[0].product_uom_qty
        res = super(MrpProductProduce, self).on_change_qty(product_qty,
                                                           consume_lines)
        if context.get('active_id') and context.get('default_mode', False) and \
                context['default_mode'] == 'consume':
            lines = []
            for move in production.move_lines:
                total = move.product_uom_qty
                for quant in move.reserved_quant_ids:
                    qty = quant.qty < total and quant.qty or total
                    lines.append([0, False, {'product_id': quant.product_id.id,
                                  'product_qty': qty,
                                  'lot_id': quant.lot_id.id,
                                  'location_id': quant.location_id.id,
                                  'move_id': move.id}])
                    total -= qty
                if total > 0:
                    lines.append([0, False, {'product_id': move.product_id.id,
                                  'location_id': move.location_id.id,
                                  'product_qty': total,
                                  'move_id': move.id}])
            res['value']['consume_lines'] = lines
        return res

    @api.multi
    def do_produce(self):
        if self.mode in ['consume_produce', 'consume']:
            self.mapped('consume_lines.move_id').do_unreserve()
            modified_moves = []
            for line in self.consume_lines.filtered(lambda r: r.product_qty > 0.0):
                if line.move_id.id in modified_moves:
                    line.create_move()
                else:
                    line.modify_move()
                    modified_moves.append(line.move_id.id)
            self.mapped('consume_lines.move_id').action_assign()
            if any(item.state not in ['assigned'] for item in self.mapped('consume_lines.move_id')):
                raise exceptions.Warning(_('Invalid Action!'), _('At least one product does not have enough stock to be consumed.'))

        return super(MrpProductProduce, self).do_produce()

class MrpProductProduceLine(models.TransientModel):

    _inherit = 'mrp.product.produce.line'

    location_id = fields.Many2one('stock.location', 'Location')
    move_id = fields.Many2one('stock.move', 'Move')

    @api.multi
    def create_move(self):
        self.ensure_one()
        self.move_id = self.move_id.copy({'restrict_lot_id': self.lot_id.id,
                                          'product_uom_qty': self.product_qty,
                                          'location_id': self.location_id.id})
        self.move_id.action_confirm()

    @api.multi
    def modify_move(self):
        self.ensure_one()
        self.move_id.write({'restrict_lot_id': self.lot_id.id,
                            'product_uom_qty': self.product_qty,
                            'location_id': self.location_id.id})
