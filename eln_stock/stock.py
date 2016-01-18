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
from openerp.osv import osv,fields

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    
    def _get_invoice_type(self, pick):
        src_usage = dest_usage = None
        inv_type = None
        if pick.invoice_state == '2binvoiced':
            if pick.move_lines:
                src_usage = pick.move_lines[0].location_id.usage
                dest_usage = pick.move_lines[0].location_dest_id.usage
            if pick.type == 'out' and dest_usage == 'supplier':
                inv_type = 'in_refund'
            elif pick.type == 'out' and dest_usage == 'customer':
                inv_type = 'out_invoice'
            elif pick.type == 'in' and src_usage == 'supplier':
                inv_type = 'in_invoice'
            elif pick.type == 'in' and src_usage == 'customer':
                inv_type = 'out_refund'
            elif pick.type == 'in':
                inv_type = 'in_invoice'
            else:
                inv_type = 'out_invoice'
        return inv_type

stock_picking()

class stock_incoterms(osv.osv):
    _inherit = "stock.incoterms" 
    #Ponemos el campo name como traducible
    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True, help="Incoterms are series of sales terms.They are used to divide transaction costs and responsibilities between buyer and seller and reflect state-of-the-art transportation practices."),
    }

stock_incoterms()

class stock_move(osv.osv):
    _inherit = 'stock.move'

    def onchange_quantity(self, cr, uid, ids, product_id, product_qty,
                          product_uom, product_uos):
        """
        Modificamos para que solo permita en unidad de medida la que tiene el producto como uom o como uom_po
        Modificamos para que solo permita en unidad de venta la que tiene el producto asignada
        Con todo esto evitamos sobre todo problemas en precios en facturas (_get_price_unit_invoice)
        """

        if product_id:
            product_obj = self.pool.get('product.product')
            product_obj = product_obj.browse(cr, uid, product_id, context=None)
            uos = product_obj.uos_id and product_obj.uos_id.id or False
            uom = product_obj.uom_id and product_obj.uom_id.id or False
            uom_po = product_obj.uom_po_id and product_obj.uom_po_id.id or False
            if product_uom not in (uom, uom_po):
                product_uom = uom
            if product_uos: #Si se pone unidad de venta tiene que ser la del producto
                product_uos = uos

        res = super(stock_move, self).onchange_quantity(cr, uid, ids, product_id, product_qty, product_uom, product_uos)

        res['value']['product_uom'] = product_uom
        res['value']['product_uos'] = product_uos

        # Cuando se abre una linea existente para editar, si ya habia pasado por aqui 
        # va a usar el dominio del articulo anterior. Si es un inconveniente eliminar todo lo que está en el if
        if product_id: 
            res['domain'] = {'product_uom': [('id', 'in', (uom, uom_po))], 'product_uos': [('id', 'in', (uos,))]} 
        else:
            res['domain'] = {'product_uom': [], 'product_uos': []} 
        
        return res

stock_move()

