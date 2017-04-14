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
from openerp.osv import osv, fields


class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'

    def get_moves(self, cr, uid, ids, context=None):
        res = []
        z = ids
        moves = self.pool.get('stock.move').search(cr, uid, [('move_history_ids2', 'in', z), ('state', '!=', 'cancel')])
        if moves:
            for move in moves:
                x = self.get_moves(cr, uid, [move])
                res.append(move)
                if x:
                    for id in x:
                        res.append(id)
        res = list(set(res))
        return res

    def get_moves_up(self, cr, uid, ids, context=None):
        res = []
        z = ids
        moves = self.pool.get('stock.move').search(cr, uid, [('move_history_ids', 'in', z),('state', '!=', 'cancel')])
        if moves:
            for move in moves:
                res.append(move)
        res = list(set(res))
        return res

    def _get_moves_traceability(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        moves = []
        if context is None: context = {}
        for line in self.browse(cr, uid, ids):
            parents = []
            if parents:
                for par in parents:
                    x = self.get_moves(cr, uid, [par])
                    moves.append(par)
                    if x:
                        for id in x:
                            moves.append(id)
            if moves:
                moves = list(set(moves))
                res[line.id] = moves

        return res

    def _get_moves_traceability_up(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        moves = []
        if context is None: context = {}
        for line in self.browse(cr, uid, ids):
            parents = []
            if parents:
                for par in parents:
                    x = self.get_moves_up(cr, uid, [par])
                    moves.append(par)
                    if x:
                        for id in x:
                            moves.append(id)
            if moves:
                moves = list(set(moves))
                res[line.id] = moves

        return res

    def _get_weight_x_qty(self, cr, uid, move_id, context=None):
        res = {}
        if context is None: context = {}
        if move_id.product_id and move_id.product_uom and move_id.product_qty:
            uom_kg = self.pool.get('product.uom').search(cr, uid, [('name', '=', 'kg')])
            if uom_kg:
                if move_id.product_uom.id <> uom_kg[0]:
                    res = move_id.product_qty * move_id.product_id.weight_net
                else:
                    res = move_id.product_qty
        return res

    def _get_balance(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        data_pool = self.pool.get('ir.model.data')
        #action_model, final_product_category = data_pool.get_object_reference(cr, uid, 'eln_production', "cat12") #Producto Final
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'entry_qty': 0.0,
                'out_qty': 0.0,
                'difference':0.0
            }
            entry_qty = 0.0
            out_qty = 0.0
            difference = 0.0
        #SE COMENTA PORQUE NO TIENE SENTIDO HACERLO DE ESTA FORMA EN LA V8. HAY QUE REVISARLO Y REHACERLO
        #    if line.stock_moves_traceability:
        #        for move in line.stock_moves_traceability:
        #            if move.location_id != move.location_dest_id:
        #                if (move.picking_id and move.picking_id.type == 'in') or \
        #                    move.production_id or move.location_id == 5 or move.location_id == 24:#revisar esto. esta puesto a dedo para salir del paso
        #                    entry_qty += self._get_weight_x_qty(cr, uid, move, context)
        #                else:
        #                    #se pone este else porque en el if siguiente no entra ya que ningun producto tiene esa
        #                    #categoria puesta. Se deja de momento así, ya que no tiene mucho sentido esta parte de
        #                    #balance de masas, pero por si se puede aprovechar en un futuro se mantiene
        #                    out_qty += self._get_weight_x_qty(cr, uid, move, context)
        #                if move.product_id and move.product_id.categ_id and move.product_id.categ_id.id == final_product_category: #los productos en realidad no tienen esta categoria. Habría que diferenciar las salidas de otra forma
        #                    out_qty += self._get_weight_x_qty(cr, uid, move, context)
        #    if entry_qty and out_qty:
        #        difference = entry_qty - out_qty

            res[line.id]['entry_qty'] = entry_qty
            res[line.id]['out_qty'] = out_qty
            res[line.id]['difference'] = difference
        return res

    _columns = {
        'stock_moves_traceability': fields.function(_get_moves_traceability, method=True, readonly=True, relation='stock.move', type="many2many", string='Moves Balance sheet of Masses'),
        'entry_qty': fields.function(_get_balance, type="float", string="Entry qty (kg)", readonly=True, digits=(16,2), multi="balance"),
        'out_qty': fields.function(_get_balance, type="float", string="Out qty (kg)", readonly=True, digits=(16,2), multi="balance"),
        'difference': fields.function(_get_balance, type="float", string="Difference (kg)", readonly=True, digits=(16,2), multi="balance"),
        'stock_moves_traceability_up': fields.function(_get_moves_traceability_up, method=True, readonly=True, relation='stock.move', type="many2many", string='Moves Balance sheet of Masses Up'),
    }
stock_production_lot()


class stock_move(osv.osv):
    _inherit = 'stock.move'

    def _get_weight_x_qty(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None: context = {}
        for line in self.browse(cr, uid, ids):
            if line.product_id and line.product_uom and line.product_qty:
                uom_kg = self.pool.get('product.uom').search(cr, uid, [('name', '=', 'kg')])
                if uom_kg:
                    if line.product_uom.id <> uom_kg[0]:
                        res[line.id] = line.product_qty * line.product_id.weight_net
                    else:
                        res[line.id] = line.product_qty
        return res

    _columns = {
        'qty_weight': fields.function(_get_weight_x_qty, type="float", string="Weight x Qty", readonly=True)
    }

stock_move()
