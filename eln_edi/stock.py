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
from openerp.osv import fields, orm


class stock_move(orm.Model):
    _inherit = 'stock.move'

    def _read_packing_id_group(self, cr, uid, ids, domain,
                               read_group_order=None, access_rights_uid=None,
                               context=None):
        moves = self.browse(cr, uid, context.get('active_ids', False), context)
        pick_ids = [x.picking_id.id for x in moves]
        access_rights_uid = access_rights_uid or uid
        packing_obj = self.pool.get('edi.packing')
        order = packing_obj._order
        if read_group_order == 'packing_id desc':
            order = "%s desc" % order
        packing_ids = packing_obj._search(
            cr, uid, [('picking_id', 'in', pick_ids)], order=order,
            access_rights_uid=access_rights_uid, context=context)
        result = packing_obj.name_get(cr, access_rights_uid, packing_ids,
                                      context=context)
        # restore order of the search
        result.sort(lambda x, y: cmp(packing_ids.index(x[0]),
                                     packing_ids.index(y[0])))
        index = 1
        for index in range(len(result)):
            lst = list(result[index])
            lst[1] += ' ' + str(index + 1)
            result[index] = tuple(lst)
        return result, {}

    _group_by_full = {
        'packing_id': _read_packing_id_group,
    }

    _columns = {
        'packing_id': fields.many2one('edi.packing', 'Packing'),
    }



class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def _check_unique_pack(self, cr, uid, ids, context=None):

        all_ok = True
        for self_obj in self.browse(cr, uid, ids, context=context):
            lst = []
            for packing in self_obj.packing_ids:
                if packing.pack_id.id not in lst:
                    lst.append(packing.pack_id.id)
            if len(lst) > 1:
                all_ok = False
        return all_ok

    _constraints = [(_check_unique_pack, 'Error: UNIQUE MSG', ['packing_ids']),]

    _columns = {
        'packing_ids': fields.one2many('edi.packing', 'picking_id', 'Packings'),
    }


class edi_packing(orm.Model):
    _name = 'edi.packing'

    _columns = {
        'picking_id': fields.many2one('stock.picking', 'Picking'),
        'move_ids': fields.one2many('stock.move', 'packing_id', 'Moves'),
        'pack_id': fields.many2one('edi.pack', 'Pack', required=True, help="Descripción codificada de la forma en la que se presentan los bienes. Se usa en mensaje DESADV. Normalmente código 201."),
        'name': fields.related('pack_id', 'name', type='char', string='Name')
    }


class edi_pack(orm.Model):
    _name = 'edi.pack'

    _columns = {
        'name': fields.char('Name', size=64),
        'code': fields.char('Code', size=3),
        'note': fields.text('Notes', readonly = False),
    }


class stock_return_picking(orm.TransientModel):
    _inherit = 'stock.return.picking'

    def default_get(self, cr, uid, fields, context=None):
        """ Precargamos el campo cantidad con la diferencia entre la cantidad, y la cantidad
        aceptada del movimiento"""
        if context is None:
            context = {}

        result1 = []
        res = super(stock_return_picking, self).default_get(cr, uid, fields, context=context)
        record_id = context and context.get('active_id', False) or False
        pick_obj = self.pool.get('stock.picking')
        pick = pick_obj.browse(cr, uid, record_id, context=context)

        if pick:
            for line in pick.move_lines:
                qty = line.product_qty - line.accepted_qty ##el return history k?? qty = line.product_qty - return_history[line.id]
                if qty > 0:
                    result1.append({'product_id': line.product_id.id, 'quantity': qty,'move_id':line.id})
            if 'product_return_moves' in fields:
                res.update({'product_return_moves': result1})

        return res

    def create_returns(self, cr, uid, ids, context=None):
        """ Escribimos el albarán de devolución relacionado al albarán
            original"""
        res = super(stock_return_picking, self).create_returns(cr, uid, ids,
                                                               context)

        record_id = context and context.get('active_id', False) or False
        pick = self.pool.get('stock.picking').browse(cr, uid, record_id,
                                                     context=context)

        if pick:
            return_pick_id = self.pool.get('stock.picking').search(
                cr, uid, [('name', 'like', "%"+pick.name+"-return")],
                context=context)
            if return_pick_id:
                pick.write({'return_picking_id': return_pick_id[0]})

        return res
