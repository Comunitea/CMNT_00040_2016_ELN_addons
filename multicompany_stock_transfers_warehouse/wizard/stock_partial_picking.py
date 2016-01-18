# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Pexego (<www.pexego.es>). All Rights Reserved
#    $Javier Colmenero Fernández$
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

from openerp.osv import osv

class stock_partial_picking(osv.osv_memory):
    _inherit = 'stock.partial.picking'

    def do_partial(self, cr, uid, ids, context=None):
        """ Makes partial moves and pickings done.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for which we want default values
        @param context: A standard dictionary
        @return: A dictionary which of fields with values.
        """
        
        if context is None:
            context = {}
        res = super(stock_partial_picking, self).do_partial(cr, uid, ids, context)
        
        pick_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        picking_ids = context.get('active_ids', False)
        partial = self.browse(cr, 1, ids[0], context=context)
        prodlot_obj = self.pool.get('stock.production.lot')

        for pick in pick_obj.browse(cr, uid, picking_ids, context=context):
            if pick.type == 'out' and pick.is_transfer:
                for move in partial.move_ids:
                    if move.move_id.related_company_move_id and move.prodlot_id: #Si tenemos lote para enviar comprobamos si ya existe en la compañía destino uno relacionado
                        lot_dest_ids = prodlot_obj.search(cr, 1, [('multicompany_prodlot_id', '=', move.prodlot_id.id)])
                        if not lot_dest_ids:
                            new_id = prodlot_obj.copy(cr, 1, move.prodlot_id.id, {'company_id': move.move_id.related_company_move_id.move_in_id.company_id.id, 'multicompany_prodlot_id': move.prodlot_id.id}, context)
                            lot_dest_ids = [new_id]
                        move_obj.write(cr, 1, move.move_id.related_company_move_id.move_in_id.id, {'prodlot_id': lot_dest_ids[0]})
        return res

stock_partial_picking()