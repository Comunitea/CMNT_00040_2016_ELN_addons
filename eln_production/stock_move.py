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
from openerp.tools.translate import _

class stock_move(osv.osv):
    _inherit = 'stock.move'

    def action_consume(self, cr, uid, ids, product_qty, location_id=False, restrict_lot_id=False, restrict_partner_id=False,
                     consumed_for=False, context=None):
        """
        Cuando en contexto le pasamos el movimiento de la producion lo arrastramos a este metodo.
        """
        if context.get('main_production_move', False):
            consumed_for = context['main_production_move']
        return super(stock_move, self).action_consume(cr, uid, ids, product_qty, 
                                                      location_id=location_id,
                                                      restrict_lot_id=restrict_lot_id,
                                                      restrict_partner_id=restrict_partner_id,
                                                      consumed_for=consumed_for,
                                                      context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}

        if isinstance(ids,(int,long)):
            ids = [ids]
        # Escribir el campo main_production_move si se le ha pasado en contexto
        # para que el action_produce de mrp.production sepa escribirlo.
        if context.get('main_production_move', False):
            vals.update({'consumed_for': context['main_production_move']})
        res = super(stock_move, self).write(cr, uid, ids, vals, context=context)
        if vals.get('prodlot_id', False):
            for move in self.browse(cr, uid, ids):
                if move.production_ids and move.production_ids[0].picking_id and move.production_ids[0].picking_id.move_lines:
                    for line in move.production_ids[0].picking_id.move_lines:
                        if line.product_id and line.product_id.id == move.product_id.id \
                                and (line.prodlot_id and line.prodlot_id.id != vals['prodlot_id'] or not line.prodlot_id):
                            self.pool.get('stock.move').write(cr, uid, line.id, {'prodlot_id': vals['prodlot_id']})
        return res


    def product_id_change_mrp_productions(self, cr, uid, ids, prod_id=False, production_name='', context=None):
        if not prod_id:
            return {}
        mrp = False
        destination_location_id = False
        source_location_id = False
        mrp = self.pool.get('mrp.production').search(cr, uid, [('name','=', production_name)])
        if mrp:
            mrp = self.pool.get('mrp.production').browse(cr, uid, mrp[0])
            destination_location_id = mrp.product_id.product_tmpl_id.property_stock_production.id
            source_location_id = mrp.location_src_id.id

        product = self.pool.get('product.product').browse(cr, uid, [prod_id], context)[0]
        uos_id  = product.uos_id and product.uos_id.id or False

        result = {
            'product_uom': product.uom_id.id,
            'product_uos': uos_id,
            'product_qty': 1.00,
            'product_uos_qty' : self.pool.get('stock.move').onchange_quantity(cr, uid, ids, prod_id, 1.00, product.uom_id.id, uos_id)['value']['product_uos_qty'],
            'name': _('PROD: %s') % production_name,
            'location_id': source_location_id,
            'location_dest_id': destination_location_id,
            'state': 'waiting',
        }

        return {'value': result}


class stock_location(osv.osv):
    _inherit = 'stock.location'
    _columns = {
        'sample_location': fields.boolean('Sample location')
    }

