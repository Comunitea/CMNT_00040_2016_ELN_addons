# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
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
from openerp import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_consume(self, product_qty, location_id=False,
        restrict_lot_id=False, restrict_partner_id=False, consumed_for=False):
        # Cuando en el contexto le pasamos el movimiento de la producción
        # lo arrastramos a este método.
        main_production_move = self._context.get('main_production_move', False)
        if main_production_move:
            consumed_for = main_production_move
        res = super(StockMove, self).action_consume(
            product_qty, location_id=location_id,
            restrict_lot_id=restrict_lot_id,
            restrict_partner_id=restrict_partner_id,
            consumed_for=consumed_for
        )
        return res

    @api.multi
    def write(self, vals):
        # Escribimos el campo main_production_move si viene en el contexto
        # para que el action_produce de mrp_production pueda escribirlo.
        main_production_move = self._context.get('main_production_move', False)
        if main_production_move:
            vals.update({'consumed_for': main_production_move})
        res = super(StockMove, self).write(vals)
        return res

    @api.multi
    def action_scrap(self, product_qty, location_id,
        restrict_lot_id=False, restrict_partner_id=False):
        # Si el movimiento que se va a desechar tiene procurement_id asociado,
        # el nuevo(s) movimiento(s) de scrap lo mantiene.
        # Con este cambio evitamos que lo herede, ya que sino provoca
        # que se tenga en cuenta en el cálculo de abastecimientos
        # en el método subtract_procurements si el abastecimiento no está
        # en estado 'cancel' o 'done', haciendo que se considere
        # como cantidad virtualmente abastecida.
        # Generalmente ocurre en producciones no 'done' 
        # (por tanto, abastecimiento en ejecución)
        # y con movimientos de scrap.
        new_moves = super(StockMove, self).action_scrap(
            product_qty, location_id, restrict_lot_id=restrict_lot_id,
            restrict_partner_id=restrict_partner_id)
        moves_to_write = self.env['stock.move'].browse(new_moves).filtered(
            lambda r: r.procurement_id and r.production_id)
        moves_to_write.write({'procurement_id': False})
        return new_moves
