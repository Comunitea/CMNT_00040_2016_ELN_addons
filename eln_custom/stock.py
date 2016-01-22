# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos All Rights Reserved
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
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def _read_group_route_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        access_rights_uid = access_rights_uid or uid
        route_obj = self.pool.get('route')
        order = route_obj._order
        if read_group_order == 'route_id desc':
            # lame hack to allow reverting search, should just work in the trivial case
            order = "%s desc" % order
        route_ids = route_obj._search(cr, uid, [], order=order,
                                      access_rights_uid=access_rights_uid, context=context)
        result = route_obj.name_get(cr, access_rights_uid, route_ids, context=context)
        # restore order of the search
        result.sort(lambda x,y: cmp(route_ids.index(x[0]), route_ids.index(y[0])))
        return result

    _group_by_full = {
        'route_id': _read_group_route_ids
    }

    def _get_color_stock(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if ids:
            for pick in self.browse(cr, uid, ids, context=context):
                res[pick.id] = 2
                if pick.state == 'draft':
                    res[pick.id] = 0
                elif pick.state == 'auto':
                    res[pick.id] = 3
                elif pick.state == 'done':
                    res[pick.id] = 6
                elif pick.state == 'assigned':
                    res[pick.id] = 7
                elif pick.state == 'confirmed':
                        res[pick.id] = 4
                elif pick.state == 'cancel':
                    res[pick.id] = 1
                else:
                    res[pick.id] = 2
        return res

    def _get_total_values(self, cr, uid, ids, field_name, arg, context=None):
        res = {}

        for picking in self.browse(cr, uid, ids, context=context):
            res[picking.id] = {
                'packages': 0.0,
                'weight': 0.0,
                'weight_net': 0.0,
                'volume': 0.0,
            }
            for line in picking.move_lines:
                res[picking.id]['packages'] += line.product_qty
                if line.product_id:
                    res[picking.id]['weight'] += line.product_id.weight
                    res[picking.id]['weight_net'] += line.product_id.weight_net
                    res[picking.id]['volume'] += line.product_id.volume
        return res

    def _get_picking(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
            result[line.picking_id.id] = True
        return result.keys()

    _columns = {
        'color_stock': fields.integer('Color stock'),
        'packages': fields.function(_get_total_values,
                                    digits_compute= dp.get_precision('Sale Price'),
                                    string='Packages', multi='sums',
                                    store = {
                                        'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['stock_move'], 10),
                                        'stock.move': (_get_picking, ['product_id', 'product_qty'], 10)
                                    }),
        'weight': fields.function(_get_total_values,
                                  digits_compute= dp.get_precision('Sale Price'),
                                  string='Weigth', multi='sums',
                                  store = {
                                      'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['stock_move'], 10),
                                      'stock.move': (_get_picking, ['product_id', 'product_qty'], 10)
                                  }),
        'weight_net': fields.function(_get_total_values,
                                      digits_compute= dp.get_precision('Sale Price'),
                                      string='Weigth Net', multi='sums',
                                      store = {
                                          'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['stock_move'], 10),
                                          'stock.move': (_get_picking, ['product_id', 'product_qty'], 10)
                                      }),
        'volume': fields.function(_get_total_values,
                                  digits_compute= dp.get_precision('Sale Price'),
                                  string='Volume', multi='sums',
                                  store = {
                                       'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['stock_move'], 10),
                                       'stock.move': (_get_picking, ['product_id', 'product_qty'], 10)
                                      }),
        'route_id': fields.many2one('route', 'Route'),
        'container_numbers': fields.related('purchase_id', 'container_numbers', type='char', string="Container numbers", readonly=True,  
                           help="Container numbers assigned to the order."),
    }
    _defaults = {
        'color_stock': 0
    }
    def onchange_route_id(self, cr, uid, ids, route_id):
        res = {'carrier_id': False}
        if not route_id:
            return {'value': res}
        route = self.pool.get('route').browse(cr, uid, route_id)
        if route.carrier_id:
            res['carrier_id'] = route.carrier_id.id
        return {'value': res}
    
stock_picking()

class stock_location(osv.osv):
    _inherit = 'stock.location'
    _description = "Location"

    _columns = {
        'name': fields.char('Location Name', size=64, required=True, translate=False),
    }

stock_location()

class stock_inventory(osv.osv):
    _inherit = "stock.inventory"
    _description = "Inventory"
    
    def action_cancel_inventory(self, cr, uid, ids, context=None):
        """ Cancels both stock move and inventory
        @return: True
        """
        """ Modificación para que no permita cancelar inventario si alguna de sus lineas ya
        tiene movimientos relacionados (stock_move_history_ids en el campo parent_id)
        Sino, se corre el riesgo de cancelar un movimiento del que ya se a descontado stock de un lote y por tanto,
        entre otras cosas, no se vería en el árbol de trazabilidad
         """
        move_obj = self.pool.get('stock.move')
        for inv in self.browse(cr, uid, ids, context=context):
            inventory_move_ids = [x.id for x in inv.move_ids]
            z = inventory_move_ids
            moves = move_obj.search(cr, uid, [('move_history_ids2', 'in', z), ('state', '!=', 'cancel')])
            if moves:
                raise osv.except_osv(_('UserError'),
                                     _('In order to cancel this inventory, if it is possible, you must first cancel the related moves.'))
                
        res = super(stock_inventory, self).action_cancel_inventory(cr, uid, ids, context=context)
        
        return res

stock_inventory()

