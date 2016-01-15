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
from osv import osv
import netsvc


class procurement_order(osv.osv):
    _inherit = "procurement.order"
    def _create_picking_and_procurement(self, cr, uid, procurement, context=None):
        move_obj = self.pool.get('stock.move')
        picking_obj=self.pool.get('stock.picking')
        wf_service = netsvc.LocalService("workflow")
        proc_obj = self.pool.get('procurement.order')
        data_pool = self.pool.get('ir.model.data')
        picking_id = picking_obj.create(cr, uid, {
                        'origin': "Procurement: %s" % procurement.name,
                        'company_id': procurement.company_id and procurement.company_id.id or False,
                        'type': 'internal',
                        'move_type': 'one',
                        'address_id': False,
                        'invoice_state': 'none',
                    })

        warehouse = self.pool.get('stock.warehouse').search(cr, uid, [('company_id','=', procurement.company_id.id)])[0]
        stock_location = self.pool.get('stock.warehouse').browse(cr, uid, warehouse).lot_stock_id.id
        action_model, samples_location = data_pool.get_object_reference(cr, uid, 'eln_product_samples', "stock_physical_location_samples2")
        move_id = move_obj.create(cr, uid, {
            'name': "Procurement: %s" % procurement.name,
            'picking_id': picking_id,
            'company_id':  procurement.company_id and procurement.company_id.id or False,
            'product_id': procurement.product_id.id,
            'product_qty': 1.0 / procurement.product_id.uos_coeff,
            'product_uom': procurement.product_uom.id or False,
            'product_uos_qty':1.0 ,
            'product_uos': procurement.product_id.uos_id and procurement.product_id.uos_id.id or procurement.product_uom.id,
            'address_id': False,
            'location_id': stock_location,
            'location_dest_id': samples_location,
            'tracking_id': False,
            'cancel_cascade': False,
            'state': 'confirmed'
        })

        proc_id = proc_obj.create(cr, uid, {
            'name':'Not enough stock for samples',
            'origin': "Procurement: %s" % procurement.name,
            'company_id': procurement.company_id and procurement.company_id.id or False,
            'product_id':  procurement.product_id.id,
            'product_qty': 1.0 / procurement.product_id.uos_coeff,
            'product_uom':procurement.product_uom.id or False,
            'product_uos_qty':1.0,
            'product_uos': procurement.product_id.uos_id and procurement.product_id.uos_id.id or procurement.product_uom.id,
            'location_id': stock_location,
            'procure_method': 'make_to_stock',
            'move_id': move_id,
        })

        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)

        wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)

        # trigger direct processing (the new procurement shares the same planned date as the original one, which is already being processed)
        wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_check', cr)

        picking_obj.force_assign(cr, uid, [picking_id])
        wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_done', cr)
        return True

    def check_make_to_stock(self, cr, uid, ids, context=None):
        """ Checks product type.
        @return: True or False
        """
        
        ok = True
        for procurement in self.browse(cr, uid, ids, context=context):
            if procurement.product_id.type == 'service':
                ok = ok and self._check_make_to_stock_service(cr, uid, procurement, context)
            else:
                ok = ok and self._check_make_to_stock_product(cr, uid, procurement, context)
                if ok == False:
                    if procurement.move_id.sale_line_id.sample_ok:
                        self._create_picking_and_procurement(cr, uid, procurement, context)

        return ok

procurement_order()