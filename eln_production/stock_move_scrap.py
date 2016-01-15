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
from osv import osv, fields


class stock_move_scrap(osv.osv_memory):
    _inherit = "stock.move.scrap"

    _columns = {
        'prodlot_id': fields.many2one('stock.production.lot', 'Lot'),
        'track_production': fields.boolean('Track production', readonly=True)
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
        if move.product_id and move.product_id.track_production:
            res.update({'track_production': True})
        if 'prodlot_id' in fields:
            if move.prodlot_id:
                res.update({'prodlot_id': move.prodlot_id.id})

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
            if data.prodlot_id:
                move_obj.write(cr, uid, move_ids, {'prodlot_id': data.prodlot_id.id}, context=context)

        super(stock_move_scrap, self).move_scrap(cr, uid, ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

stock_move_scrap()

