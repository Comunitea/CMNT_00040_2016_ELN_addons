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

class split_in_production_lot(osv.osv_memory):
    _inherit = "stock.move.split"

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(split_in_production_lot, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id'):
            move = self.pool.get('stock.move').browse(cr, uid, context['active_id'], context=context)
            if 'product_uos' in fields:
                res.update({'product_uos': move.product_uos.id})
            if 'qty_uos' in fields:
                res.update({'qty_uos': move.product_uos_qty})
        return res

    _columns = {
        'qty_uos': fields.float('Quantity (UoS)', digits_compute=dp.get_precision('Product UoM')),
        'product_uos': fields.many2one('product.uom', 'UoS'),
     }


split_in_production_lot()

class stock_move_split_lines_exist(osv.osv_memory):
    _inherit = "stock.move.split.lines"

    _columns = {
        'quantity_uos': fields.float('Quantity (UoS)', digits_compute=dp.get_precision('Product UoM')),
    }
    _defaults = {
        'quantity_uos': 1.0,
    }
    
    def onchange_lot_id2(self, cr, uid, ids, prodlot_id=False, product_qty=False,
                        loc_id=False, product_id=False, uom_id=False, qty=False, qty_uos=False):

        res = self.onchange_lot_id(cr, uid, ids, prodlot_id, product_qty, loc_id, product_id, uom_id)

        if qty and qty_uos:
            qty_converted = 1.0 * product_qty * qty_uos / (qty or 1.0)
            if not res.get('value', False):
                res = {'value': {}}
            if res['value'].get('quantity_uos', False):
                res['value']['quantity_uos'] = qty_converted
            else:
                res['value'].update({'quantity_uos': qty_converted})
            
        return res

    def onchange_quantity(self, cr, uid, ids, product_qty=False, product_qty_uos=False, qty=False, qty_uos=False):

        res = {}
        
        if product_qty and not product_qty_uos:
            qty_converted = 1.0 * product_qty * qty_uos / (qty or 1.0)
            res['quantity_uos'] = qty_converted
        else:
            qty_converted = 1.0 * product_qty_uos * qty / (qty_uos or 1.0)
            res['quantity'] = qty_converted

        return {'value': res}
    
stock_move_split_lines_exist()
