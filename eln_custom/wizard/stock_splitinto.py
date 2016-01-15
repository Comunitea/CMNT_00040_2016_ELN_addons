# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import fields, osv
from tools.translate import _
import decimal_precision as dp

class stock_split_into(osv.osv_memory):
    _inherit = "stock.split.into"

    def split(self, cr, uid, data, context=None):
        """Sustituimos la función original para que guarde la cantidad de producto 
        en la unidad de venta de forma correcta. 
        Antes guardaba lo mismo que para la unidad de medida por defecto"""

        if context is None:
            context = {}

        inventory_id = context.get('inventory_id', False)
        rec_id = context and context.get('active_ids', False)
        move_obj = self.pool.get('stock.move')
        track_obj = self.pool.get('stock.tracking')
        inventory_obj = self.pool.get('stock.inventory')
        quantity = self.browse(cr, uid, data[0], context=context).quantity or 0.0
        for move in move_obj.browse(cr, uid, rec_id, context=context):
            quantity_rest = move.product_qty - quantity
            uos_qty = quantity / move.product_qty * move.product_uos_qty
            uos_qty_rest = quantity_rest / move.product_qty * move.product_uos_qty
            #if move.tracking_id :
            #    raise osv.except_osv(_('Error!'),  _('The current move line is already assigned to a pack, please remove it first if you really want to change it ' \
            #                        'for this product: "%s" (id: %d)') % \
            #                        (move.product_id.name, move.product_id.id,))
            if quantity > move.product_qty:
                raise osv.except_osv(_('Error!'),  _('Total quantity after split exceeds the quantity to split ' \
                                    'for this product: "%s" (id: %d)') % \
                                    (move.product_id.name, move.product_id.id,))
            if quantity > 0:
                move_obj.setlast_tracking(cr, uid, [move.id], context=context)
                move_obj.write(cr, uid, [move.id], {
                    'product_qty': quantity,
                    'product_uos_qty': uos_qty,
                    'product_uos': move.product_uos.id,
                })

            if quantity_rest>0:
                quantity_rest = move.product_qty - quantity
                tracking_id = track_obj.create(cr, uid, {}, context=context)
                if quantity == 0.0:
                    move_obj.write(cr, uid, [move.id], {'tracking_id': tracking_id}, context=context)
                else:
                    default_val = {
                        'product_qty': quantity_rest,
                        'product_uos_qty': uos_qty_rest,
                        'tracking_id': tracking_id,
                        'state': move.state,
                        'product_uos': move.product_uos.id
                    }
                    current_move = move_obj.copy(cr, uid, move.id, default_val, context=context)
                    if inventory_id and current_move:
                        inventory_obj.write(cr, uid, inventory_id, {'move_ids': [(4, current_move)]}, context=context)

        return {'type': 'ir.actions.act_window_close'}
    
stock_split_into()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
