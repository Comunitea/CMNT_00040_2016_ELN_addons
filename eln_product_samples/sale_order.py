# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved.
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, orm


class sale_order_line(orm.Model):
    
    _inherit = 'sale.order.line'
    _columns = {
        'sample_ok': fields.boolean('Sample?'),
    }
    
    _defaults = {
        'sample_ok': False,
    }

    def onchange_sample_ok(self, cr, uid, ids, sample_ok, price_unit, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        """
            Sets sale line price unit to zero if 'sample_ok' field is check
        """
        res = {}
        
        assert isinstance(ids, list)
        if product:
            if sample_ok:
                res['price_unit'] = 0.0
            else:
                result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging, fiscal_position, flag, context)
                result = result.get('value', {})
                res['price_unit'] = result.get('price_unit') or False
            return {'value': res}

        return res


class sale_order(orm.Model):

    _inherit = 'sale.order'

    def action_ship_create(self, cr, uid, ids, *args):
        """
            Extend this method for updating stock move based on sale_order_line 'sample' field...
        """
        assert isinstance(ids,list)
        res = super(sale_order, self).action_ship_create(cr, uid, ids, *args)
        stock_move_facade = self.pool.get('stock.move')
        data_pool = self.pool.get('ir.model.data')
        current_order = self.browse(cr, uid, ids)[0]
        sample_line_ids = []
        #Recojo el 'stock_move' del pedido que corresponda a la(s) linea(s) de muestra y le cambio la ubicación de destino...
        for line in current_order.order_line:
            if line.sample_ok:
                sample_line_ids.append(line.id)
        moves_to_upgrade = []
        
        for pick in current_order.picking_ids:
            for move in pick.move_lines:
                if move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.id in sample_line_ids:
                    moves_to_upgrade.append(move.id)

            action_model, samples_location = data_pool.get_object_reference(cr, uid, 'eln_product_samples', "stock_physical_location_samples2")
            if samples_location:
                stock_move_facade.write(cr, uid, moves_to_upgrade, {'location_id': samples_location})
        return res

    def check_sample(self, cr, uid, ids, context=None):
        """ Checks if the samples included in the sale order are correct or not.
        @return: True if correct or False if not.
        """
        products = {}
        samples = {}
        for sale in self.browse(cr, uid, ids, context=context):
            for line in sale.order_line:
                if products.get(line.product_id.id) :
                    products[line.product_id.id] = [products[line.product_id.id][0]+line.price_subtotal, products[line.product_id.id][1]+line.product_uom_qty]
                else:
                    products[line.product_id.id] = [line.price_subtotal, line.product_uom_qty]
                if line.sample_ok:
                    if samples.get(line.product_id.id) :
                        samples[line.product_id.id] = samples[line.product_id.id] + line.product_uom_qty
                    else:
                        samples[line.product_id.id] = line.product_uom_qty
        return True

