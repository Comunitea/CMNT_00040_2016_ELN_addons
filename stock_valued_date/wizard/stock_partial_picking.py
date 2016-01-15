# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2004-2012 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
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

from osv import fields, osv
import decimal_precision as dp

class stock_partial_picking_line(osv.TransientModel):

    _inherit = "stock.partial.picking.line"
    
    _columns = {
        'quantity_uos': fields.float('Quantity (UoS)', digits_compute=dp.get_precision('Product UoM')),
        'product_uos': fields.many2one('product.uom', 'Product UoS'),
    }

    def onchange_quantity(self, cr, uid, ids, product_id, product_qty,
                          product_uom, product_uos):
        """ On change of product quantity finds UoM and UoS quantities
        @param product_id: Product id
        @param product_qty: Changed Quantity of product
        @param product_uom: Unit of measure of product
        @param product_uos: Unit of sale of product
        @return: Dictionary of values
        """
        result = {
                  'quantity_uos': 0.00
          }

        if (not product_id) or (product_qty <= 0.0):
            return {'value': result}

        product_obj = self.pool.get('product.product')
        uos_coeff = product_obj.read(cr, uid, product_id, ['uos_coeff']) or 1.0

        uom_base_id = product_obj.browse(cr, uid, product_id).uom_id.id
        product_qty_uom = self.pool.get('product.uom')._compute_qty(cr, uid, product_uom, product_qty, uom_base_id)

        if product_uos and product_uom and (product_uom != product_uos):
            result['quantity_uos'] = product_qty_uom * uos_coeff['uos_coeff']
        else:
            result['quantity_uos'] = product_qty

        return {'value': result}
    
    def onchange_uos_quantity(self, cr, uid, ids, product_id, product_uos_qty,
                          product_uos, product_uom):
        """ On change of product quantity finds UoM and UoS quantities
        @param product_id: Product id
        @param product_uos_qty: Changed UoS Quantity of product
        @param product_uom: Unit of measure of product
        @param product_uos: Unit of sale of product
        @return: Dictionary of values
        """
        result = {
                  'quantity': 0.00
          }

        if (not product_id) or (product_uos_qty <= 0.0):
            return {'value': result}

        product_obj = self.pool.get('product.product')
        uos_coeff = product_obj.read(cr, uid, product_id, ['uos_coeff'])
        
        uom_base_id = product_obj.browse(cr, uid, product_id).uom_id.id

        if product_uos and product_uom and (product_uom != product_uos):
            result['quantity'] = self.pool.get('product.uom')._compute_qty(cr, uid, uom_base_id, (product_uos_qty / uos_coeff['uos_coeff']), product_uom)
        else:
            result['quantity'] = product_uos_qty

        return {'value': result}

    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False,
                            loc_dest_id=False, address_id=False):
        """ On change of product id, if finds UoM, UoS, quantity and UoS quantity.
        @param prod_id: Changed Product id
        @param loc_id: Source location id
        @param loc_dest_id: Destination location id
        @param address_id: Address id of partner
        @return: Dictionary of values
        """
        if not prod_id:
            return {}

        if not address_id:
            partial_picking_obj = self.pool.get('stock.partial.picking.line').browse(cr, uid, ids[0])
            address_id = self.pool.get('stock.move').browse(cr, uid, partial_picking_obj.move_id.id).address_id.id
            
        lang = False
        addr_rec = self.pool.get('res.partner.address').browse(cr, uid, address_id)
        if addr_rec:
            lang = addr_rec.partner_id and addr_rec.partner_id.lang or False
        ctx = {'lang': lang}

        product = self.pool.get('product.product').browse(cr, uid, [prod_id], context=ctx)[0]
        uos_id  = product.uos_id and product.uos_id.id or False
        result = {
            'product_uom': product.uom_id.id,
            'product_uos': uos_id,
            'quantity': 1.00,
            'quantity_uos' : self.pool.get('stock.partial.picking.line').onchange_quantity(cr, uid, ids, prod_id, 1.00, product.uom_id.id, uos_id)['value']['quantity_uos']
        }
        if not ids:
            result['name'] = product.partner_ref
        if loc_id:
            result['location_id'] = loc_id
        if loc_dest_id:
            result['location_dest_id'] = loc_dest_id
        
        return {'value': result}

stock_partial_picking_line()

class stock_partial_picking(osv.osv_memory):

    _inherit = "stock.partial.picking"

    def _partial_move_for(self, cr, uid, move):

        partial_move = super(stock_partial_picking, self)._partial_move_for(cr, uid, move)
        partial_move['quantity_uos'] = move.state in ('assigned','draft') and move.product_uos_qty or 0.0
        partial_move['product_uos'] = move.product_uos.id
        
        return partial_move

stock_partial_picking()

