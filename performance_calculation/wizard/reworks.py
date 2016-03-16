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
from openerp.osv import orm, fields
from openerp.addons.decimal_precision import decimal_precision as dp
import time
from datetime import datetime
from openerp.tools.translate import _


class recover_full_product(orm.TransientModel):

    _name = "recover.full.product"
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'qty_available': fields.float('Qty available', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'qty_recover': fields.float('Qty recover', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'product_uom': fields.many2one('product.uom', 'UoM', required=True),
        'current_prodlot_id': fields.many2one('stock.production.lot', 'Current Lot'),
        'recover_prodlot_id': fields.many2one('stock.production.lot', 'Recover Lot', required=True),
        'location_dest_id': fields.many2one('stock.location', 'Location dest.', required=True),
        'move_id': fields.many2one('stock.move', 'Source Move', required=True)
    }

    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}

        res = super(recover_full_product, self).default_get(cr, uid, fields, context=context)

        move = self.pool.get('stock.move').browse(cr, uid, context.get('active_id', False), context=context)

        if move:
            res['move_id'] = move.id
            res['product_id'] = move.product_id.id
            res['qty_available'] = move.product_uom_qty
            res['product_uom'] = move.product_uom.id
            # res['current_prodlot_id'] = move.prodlot_id.id

        return res

    def recover_full_product(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        for cur in self.browse(cr, uid, ids, context):
            if cur.qty_recover > cur.qty_available:
                raise orm.except_orm(_('Error'), _('The recovery quantity must be less than or equal to the quantity available!'))

            new_id = self.pool.get('stock.move').create(cr, uid, {
                                                    'name': 'Rework of move: ' + cur.move_id.name,
                                                    'location_id': cur.move_id.location_dest_id.id,
                                                    'location_dest_id': cur.location_dest_id.id,
                                                    'product_id': cur.product_id.id,
                                                    'prodlot_id': cur.recover_prodlot_id.id,
                                                    'product_uom_qty': cur.qty_recover,
                                                    'product_uom': cur.product_uom.id,
                                                    'date_moved': time.strftime('%Y-%m-%d'),
                                                    'date': datetime.strptime(cur.move_id.date, '%Y-%m-%d %H:%M:%S'),
                                                    'move_history_ids': [],
                                                    'move_history_ids2': [],
                                                    'state': 'draft',
                                                    'reworked': False})
            self.pool.get('stock.move').action_confirm(cr, uid, [new_id], context=context)
            self.pool.get('stock.move').action_done(cr, uid, [new_id], context=context)

            if cur.qty_recover < cur.qty_available:
                new_id2 = self.pool.get('stock.move').copy(cr, uid, cur.move_id.id, {'product_uom_qty': cur.qty_available - cur.qty_recover , 'reworked': True})
                self.pool.get('stock.move').write(cr, uid, [cur.move_id.id], {
                                                    'move_history_ids': [(6,0, [new_id,new_id2])],
                                                    'reworked': False})
            else:
                self.pool.get('stock.move').write(cr, uid, [cur.move_id.id], {
                                                    'move_history_ids': [(4, new_id)],
                                                    'reworked': False})
        return {'type': 'ir.actions.act_window_close'}


class recover_components(orm.TransientModel):

    _name = 'recover.components'
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'composition_lines_ids': fields.one2many('recover.components.composition', 'parent_id', 'Composition'),
        'move_id': fields.many2one('stock.move', 'Source Move', required=True)
    }

    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}

        result = []
        res = super(recover_components, self).default_get(cr, uid, fields, context=context)

        move = self.pool.get('stock.move').browse(cr, uid, context.get('active_id', False), context=context)

        if move:
            res['move_id'] = move.id
            res['product_id'] = move.product_id.id

            if move.product_id.bom_ids:
                bom = move.product_id.bom_ids[0]
                factor = move.product_uom_qty * move.product_uom.factor / bom.product_uom.factor
                res1, res2 = self.pool.get('mrp.bom')._bom_explode(cr, uid, bom, move.product_id, factor, properties=[])#, addthis=False, level=0, routing_id=False)

                for r in res1:
                    vals = {'product_id': r['product_id'],
                            'qty_available': r['product_qty'],
                            'product_uom': r['product_uom']
                    }
                    c_id = self.pool.get("recover.components.composition").create(cr, uid, vals)
                    result.append(c_id)
                res['composition_lines_ids'] = result
        return res

    def recover_components(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        new_ids = []

        for cur in self.browse(cr, uid, ids, context):
            if cur.composition_lines_ids:
                for line in cur.composition_lines_ids:
                    if line.recover:
                        if line.qty_recover > line.qty_available:
                            raise orm.except_orm(_('Error'), _('The recovery quantity must be less than or equal to the quantity available!'))
                        new_id = self.pool.get('stock.move').create(cr, uid, {
                                                    'name': 'Rework of move: ' + cur.move_id.name,
                                                    'product_id': line.product_id.id,
                                                    'location_id': cur.move_id.location_dest_id.id,
                                                    'location_dest_id': line.location_dest_id.id,
                                                    'prodlot_id': line.recover_prodlot_id.id,
                                                    'product_uom_qty': line.qty_recover,
                                                    'product_uom': line.product_uom.id,
                                                    'date_moved': time.strftime('%Y-%m-%d'),
                                                    'date': datetime.strptime(cur.move_id.date, '%Y-%m-%d %H:%M:%S'),
                                                    'move_history_ids': [],
                                                    'move_history_ids2': [],
                                                    'state': 'draft',
                                                    'reworked': False})

                        new_ids.append(new_id)
                        if line.qty_recover < line.qty_available:
                            new_id2 = self.pool.get('stock.move').copy(cr, uid, new_id, {'product_uom_qty': line.qty_available - line.qty_recover ,
                                                                                        'reworked': True,
                                                                                        'location_id':cur.move_id.location_id.id,
                                                                                        'location_dest_id':cur.move_id.location_dest_id.id,
                                                                                        'prodlot_id': False
                                                                                         })
                            new_ids.append(new_id2)
                    else:
                        new_id3 = self.pool.get('stock.move').create(cr, uid, {
                                                    'name': 'Rework of move: ' + cur.move_id.name,
                                                    'product_id': line.product_id.id,
                                                    'location_id':cur.move_id.location_id.id,
                                                    'location_dest_id':cur.move_id.location_dest_id.id,
                                                    'prodlot_id': line.recover_prodlot_id.id,
                                                    'product_uom_qty': line.qty_available,
                                                    'product_uom': line.product_uom.id,
                                                    'date_moved': time.strftime('%Y-%m-%d'),
                                                    'date': datetime.strptime(cur.move_id.date, '%Y-%m-%d %H:%M:%S'),
                                                    'move_history_ids': [],
                                                    'move_history_ids2': [],
                                                    'state': 'draft',
                                                    'reworked': True})

                        new_ids.append(new_id3)
            if new_ids:
                self.pool.get('stock.move').action_confirm(cr, uid, new_ids, context=context)
                self.pool.get('stock.move').action_done(cr, uid, new_ids, context=context)

                self.pool.get('stock.move').write(cr, uid, [cur.move_id.id], {
                                                    'move_history_ids': [(6,0, new_ids)],
                                                    'reworked': False})

        return {'type': 'ir.actions.act_window_close'}


class recover_components_composition(orm.TransientModel):

    _name = 'recover.components.composition'
    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'qty_available': fields.float('Qty available', digits_compute=dp.get_precision('Product Unit of Measure')),
        'qty_recover': fields.float('Qty recover', digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_uom': fields.many2one('product.uom', 'UoM'),
        'recover_prodlot_id': fields.many2one('stock.production.lot', 'Recover Lot' ),
        'location_dest_id': fields.many2one('stock.location', 'Location dest.'),
        'recover': fields.boolean('Recover'),
        'parent_id': fields.many2one('recover.components', 'Recover components')
    }


class stock_move_scrap(orm.TransientModel):
    _name = "stock.move.rework.scrap"
    _description = "Scrap Products"
    _inherit = "stock.move.consume"

    _defaults = {
        'location_id': lambda *x: False
    }

    def default_get(self, cr, uid, fields, context=None):
        """ Get default values
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for default value
        @param context: A standard dictionary
        @return: default values of fields
        """
        if context is None:
            context = {}
        res = super(stock_move_scrap, self).default_get(cr, uid, fields, context=context)
        move = self.pool.get('stock.move').browse(cr, uid, context['active_id'], context=context)
        location_obj = self.pool.get('stock.location')
        scraped_location_ids = location_obj.search(cr, uid, [('scrap_location','=',True)])

        if 'product_id' in fields:
            res.update({'product_id': move.product_id.id})
        if 'product_uom' in fields:
            res.update({'product_uom': move.product_uom.id})
        if 'product_uom_qty' in fields:
            res.update({'product_uom_qty': move.product_uom_qty})
        if 'location_id' in fields:
            if scraped_location_ids:
                res.update({'location_id': scraped_location_ids[0]})
            else:
                res.update({'location_id': False})

        return res

    def move_scrap(self, cr, uid, ids, context=None):
        """ To move scrapped products
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs if we want more than one
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        move_ids = context['active_ids']
        for data in self.browse(cr, uid, ids):
            quantity = data.product_qty
            location_id = data.location_id.id
            if quantity <= 0:
                raise orm.except_orm(_('Warning!'), _('Please provide a positive quantity to scrap!'))
            res = []
            for move in move_obj.browse(cr, uid, move_ids):
                move_qty = move.product_uom_qty
                uos_qty = quantity / move_qty * move.product_uos_qty
                default_val = {
                    'product_uom_qty': quantity,
                    'product_uos_qty': uos_qty,
                    'state': move.state,
                    'scrapped' : True,
                    'location_dest_id': location_id,
                    # 'tracking_id': move.tracking_id.id,
                    # 'prodlot_id': move.prodlot_id.id,
                    'reworked': False,
                    'location_id': move.location_dest_id.id
                }

                new_move = move_obj.copy(cr, uid, move.id, default_val)
                move_obj.write(cr, uid, move.id, {'reworked': False, 'move_history_ids': [(6,0, [new_move])]})
                res += [new_move]
                product_obj = self.pool.get('product.product')
                for (id, name) in product_obj.name_get(cr, uid, [move.product_id.id]):
                    self.log(cr, uid, move.id, "%s x %s %s" % (quantity, name, _("were scrapped")))

        move_obj.action_done(cr, uid, res, context=context)

        return {'type': 'ir.actions.act_window_close'}

