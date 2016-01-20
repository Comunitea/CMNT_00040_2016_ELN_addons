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

from osv import osv, fields
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tools.translate import _
import time

class sale_order(osv.osv):
    _inherit = 'sale.order'
    
    def _prepare_order_line_move(self, cr, uid, order, line, picking_id, date_planned, context=None):

        res = super(sale_order, self)._prepare_order_line_move(cr, uid, order, line, picking_id, date_planned, context=None)
        
        if line.pre_prodlot:
            prodlot_obj = self.pool.get('stock.production.lot')
            lot_id = prodlot_obj.search(cr, uid, [('name', '=', line.pre_prodlot), ('product_id', '=', line.product_id.id)])
            if lot_id:
                res.update({'prodlot_id': lot_id[0]})

        return res

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'origin': '',
        })
        return super(sale_order, self).copy(cr, uid, id, default, context)

sale_order()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    _columns = {
        'pre_prodlot': fields.char('Pre Production Lot', help="This lot is used to try to assign a existing lot in the picking output if possible.", size=64),
    }
    
    _defaults = {
        'pre_prodlot': False,
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'pre_prodlot': False,
        })
        return super(sale_order_line, self).copy_data(cr, uid, id, default, context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'pre_prodlot': False,
        })
        return super(sale_order_line, self).copy(cr, uid, id, default, context=context)

sale_order_line()
