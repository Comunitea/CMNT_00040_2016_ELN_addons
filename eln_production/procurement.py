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

from openerp.osv import osv, fields

class procurement_order(osv.osv):
    _inherit = 'procurement.order'

    def _prepare_mo_vals(self, cr, uid, procurement, context=None):
        res = super(procurement_order, self)._prepare_mo_vals(cr, uid, procurement, context=context)
        if res:
            product_obj = self.pool.get('product.product')
            virtual_available = product_obj._product_available(cr, uid, [procurement.product_id.id],
                context={'location': procurement.location_id.id})[procurement.product_id.id]['virtual_available']

            orderpoint_obj = self.pool.get('stock.warehouse.orderpoint') 
            company_id = res.get('company_id', False) or procurement[0].company_id.id
            dom = company_id and [('company_id', '=', company_id)] or []
            dom.append(('product_id', '=', procurement.product_id.id))
            orderpoint_ids = orderpoint_obj.search(cr, uid, dom)
            min_qty = max_qty = security_qty = 0
            if orderpoint_ids:
                op = orderpoint_obj.browse(cr, uid, orderpoint_ids[0], context=context)
                min_qty = min(op.product_min_qty, op.product_max_qty)
                max_qty = max(op.product_min_qty, op.product_max_qty)
                security_qty = op.product_security_qty
            
            if virtual_available <= 0:
                res.update(priority='2') #Urgente
            elif virtual_available <= security_qty:
                res.update(priority='1') #Normal
            elif virtual_available <= min_qty:
                res.update(priority='0') #No urgente
            else:
                res.update(priority='0') #No urgente

        return res
        
procurement_order()
