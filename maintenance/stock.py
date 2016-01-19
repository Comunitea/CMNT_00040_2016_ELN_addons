# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos All Rights Reserved
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
#############################################################################
from openerp.osv import fields, orm

class stock(orm.Model):
    def _work_done(self, cr, uid, ids, name, arg=None, context=None):
        res = {}
        for stock_move_id in ids:
            stock_move = self.pool.get('stock.move').browse(cr, uid, stock_move_id, context)
            res[stock_move_id] = False
            if stock_move.work_order_id:
                work_order_state = stock_move.work_order_id.state
                if work_order_state == 'done':
                    res[stock_move_id] = True
        return res

    _inherit = 'stock.move'
    _columns = {
            'element_id':fields.many2one('maintenance.element', 'Element', required=False),
            'work_order_id':fields.many2one('work.order', 'Work order', required=False),
            'work_done': fields.function(_work_done, method=True, type='boolean', string='Order completed', store=False),
                    }

    def create(self, cr, uid, vals, context=None):
        res = super(stock, self).create(cr, uid, vals, context=context)
        if vals.get('work_order_id', False) and not vals.get('picking_id', False):
            self._picking_assign(cr, uid, [res], False, vals['location_id'], vals['location_dest_id'], context={'work_order': vals['work_order_id']})

        return res

    def _picking_assign(self, cr, uid, move_ids, procurement_group, location_from, location_to, context=None):
        if context is None:
            context = {}
        if context.get('work_order'):
            pick_obj = self.pool.get("stock.picking")
            picks = pick_obj.search(cr, uid, [
                    ('work_order_id', '=', context['work_order']),
                    ('location_id', '=', location_from),
                    ('location_dest_id', '=', location_to),
                    ('state', 'in', ['draft', 'confirmed', 'waiting'])], context=context)
            if picks:
                pick = picks[0]
            else:
                move = self.browse(cr, uid, move_ids, context=context)[0]
                values = {
                    'origin': move.origin,
                    'company_id': move.company_id and move.company_id.id or False,
                    'move_type': move.group_id and move.group_id.move_type or 'direct',
                    'partner_id': move.partner_id.id or False,
                    'picking_type_id': move.picking_type_id and move.picking_type_id.id or False,
                    'work_order_id': context['work_order']
                }
                pick = pick_obj.create(cr, uid, values, context=context)
            return self.write(cr, uid, move_ids, {'picking_id': pick}, context=context)
        else:
            return super(stock, self)._picking_assign(cr, uid, move_ids, procurement_group, location_from, location_to, context=context)

class stock_picking(orm.Model):

    def _work_done(self, cr, uid, ids, name, arg=None, context=None):
        res = {}
        for stock_picking_id in ids:
            stock_picking = self.pool.get('stock.picking').browse(cr, uid, stock_picking_id, context)
            res[stock_picking_id] = False
            if stock_picking.work_order_id:
                work_order_state = stock_picking.work_order_id.state
                if work_order_state == 'done':
                    res[stock_picking_id] = True
        return res

    _inherit = 'stock.picking'
    _columns = {
            'work_order_id':fields.many2one('work.order', 'Work order', required=False),
            'work_done': fields.function(_work_done, method=True, type='boolean', string='Order completed', store=False),
                    }
