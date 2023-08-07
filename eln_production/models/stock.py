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
from openerp import models, fields, api, _
from datetime import timedelta
import openerp.addons.decimal_precision as dp


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    extended_shelf_life_date = fields.Datetime('Extended shelf life',
        help='This is the extended shelf life date.')
    product_expected_use = fields.Selection([
        ('raw', 'Raw materials'),
        ('auxiliary', 'Auxiliary materials'),
        ('packaging', 'Packaging materials'),
        ('semifinished', 'Semi-finished goods'),
        ('finished', 'Finished goods')], string='Expected use',
        related='product_id.categ_id.recursively_expected_use')

    @api.model
    def create(self, vals):
        res = super(StockProductionLot, self).create(vals)
        if not vals.get('extended_shelf_life_date', False):
            res.update_extended_shelf_life_date()
        return res

    @api.multi
    def update_extended_shelf_life_date(self):
        for lot_id in self:
            date = False
            if lot_id.use_date and lot_id.product_expected_use == 'raw':
                use_date = fields.Datetime.from_string(lot_id.use_date)
                duration = lot_id.product_id.extended_shelf_life_time or 0
                date = use_date + timedelta(days=duration)
            lot_id.extended_shelf_life_date = date

    @api.onchange('use_date')
    def onchange_use_date(self):
        if self.product_expected_use == 'raw':
            if self._origin:
                msg = _('If the best before date is changed, perhaps you should update the extended shelf life date.')
                msg += _('\nTo do this automatically, remove the extended shelf life date and the new date will be recalculated.')
                warning = {
                    'title': _('Warning!'),
                    'message': msg
                }
                return {'warning': warning}
            else:
                self.update_extended_shelf_life_date()

    @api.onchange('extended_shelf_life_date')
    def onchange_extended_shelf_life_date(self):
        if self.product_expected_use == 'raw':
            if self._origin and not self.extended_shelf_life_date:
                self.update_extended_shelf_life_date()

    @api.multi
    def action_production_related_lots(self):
        """
        Muestra los lotes usados en una producción
        para producir el lote seleccionado.
        """
        quant_obj = self.env['stock.quant']
        user_company_ids = self.env.user.company_id
        user_company_ids += user_company_ids.child_ids
        domain = [
            ('lot_id', 'in', self._ids),
            ('company_id', 'in', user_company_ids._ids)
        ]
        quants = quant_obj.search(domain)
        moves = quants.mapped('history_ids').filtered(
            lambda r: r.parent_ids and r.production_id)
        lot_ids = moves.mapped('parent_ids').mapped('quant_ids.lot_id')
        if not lot_ids:
            return {'type': 'ir.actions.act_window_close'}
        value = {
            'domain': str([('id', 'in', lot_ids.ids)]),
            'name': _('Serial Number'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.production.lot',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'res_id': lot_ids.ids if len(lot_ids.ids) > 1 else lot_ids[0].id,
        }
        return value


class StockMove(models.Model):
    _inherit = 'stock.move'

    consumed_for = fields.Many2one(select=True) # Redefine index

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


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    product_security_qty = fields.Float('Security Quantity',
        digits=dp.get_precision('Product Unit of Measure'), required=True,
        help="Security stock to determine priority on procurement orders.")

