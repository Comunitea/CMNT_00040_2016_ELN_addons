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
from openerp.osv import orm, fields

class purchase(orm.Model):

    def _work_done(self, cr, uid, ids, name, arg=None, context=None):
        res = {}
        for purchase_order_id in ids:
            purchase_order = self.pool.get('purchase.order').browse(cr, uid, purchase_order_id, context)
            res[purchase_order_id] = False
            if purchase_order.work_order_id:
                work_order_state = purchase_order.work_order_id.state
                if work_order_state == 'done':
                    res[purchase_order_id] = True
        return res
    _inherit = 'purchase.order'
    _columns = {
            'work_order_id':fields.many2one('work.order', 'Work order', required=False),
            'work_done': fields.function(_work_done, method=True, type='boolean', string='order completed', store=False),
                    }

class purchase_order_line(orm.Model):
    _inherit = 'purchase.order.line'
    _columns = {
            'element_id': fields.many2one('maintenance.element', 'Element', required=False),
                }

