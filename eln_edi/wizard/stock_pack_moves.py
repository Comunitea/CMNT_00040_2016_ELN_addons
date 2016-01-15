# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Pexego All Rights Reserved
#    $Jesús Ventosinos Mayor <jesus@pexego.es>$
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
from tools.translate import _


class stock_pack_moves(osv.osv_memory):

    _name = 'stock.pack.moves'
    _columns = {
        'picking_id': fields.many2one('stock.picking', 'Picking', required=True),
        'pack_id': fields.many2one('edi.pack', 'Pack', required=True),
        'qty': fields.integer('Quantity'),
        'auto_settled': fields.boolean(''),
    }

    def show(self, cr, uid, ids, context={}):
        packing_obj = self.pool.get('edi.packing')
        for wiz in self.browse(cr, uid, ids, context):
            for count in range(wiz.qty - len(wiz.picking_id.packing_ids)):
                packing_obj.create(cr, uid,
                                   {'picking_id': wiz.picking_id.id,
                                    'pack_id': wiz.pack_id.id}, context)
        view_id = self.pool.get('ir.model.data').get_object(cr, uid, 'eln_edi', 'move_packing_kanban').id
        context['active_ids'] = [x.id for x in wiz.picking_id.move_lines]
        return {
            'name':_("Move packing"),
            'view_mode': 'kanban',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'stock.move',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [x.id for x in wiz.picking_id.move_lines])],
            'context': context
        }

    def onchange_picking_id(self, cr, uid, ids, picking_id, context=None):

        res = {'pack_id': False, 'auto_settled': False}
        picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context)
        if picking.packing_ids:
            res['qty'] = len(picking.packing_ids)
            res['pack_id'] = picking.packing_ids[0].pack_id.id
            res['auto_settled'] = True

        return {'value': res}


stock_pack_moves()
