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
import decimal_precision as dp

class weighted_average_price(osv.osv):
    _name = 'weighted.average.price'
    _description = 'Records, for each product, the PMP and the stock in a date.'

    def _product_qty_available(self, cr, uid, ids, field_names, arg, context=None):
        if context is None:
            context = {}
        c = context.copy()
        res = {}

        for line in self.browse(cr, uid, ids, context=context):
            c.update({'to_date': line.date})
            res[line.id] = self.pool.get('product.product').browse(cr, uid, line.product_id.id, context=c).qty_available
        return res

    _columns = {
        'name': fields.char('Name', size=20, required=True, readonly=True),
        'product_id': fields.many2one('product.product', 'Product', required=True,readonly=True),
        'date': fields.datetime('Date', required=True,readonly=True),
        'pmp': fields.float('PMP', digits_compute=dp.get_precision('Purchase Price'), required=True,readonly=True),
        'move_id': fields.many2one('stock.move', 'Stock move', required=True,readonly=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'stock_qty': fields.function(_product_qty_available, type='float', string='Stock qty.'),
        'pmp_old': fields.float('PMP Old', digits_compute=dp.get_precision('Purchase Price'), readonly=True),

    }
    _defaults = {
        'name': "_CODE AUTOGENERATE"
    }
    def create(self, cr, uid, vals, context=None):
        if vals.get('name', "_CODE AUTOGENERATE") == '_CODE AUTOGENERATE':
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'weighted.average.price')
            vals['name'] = sequence

        return super(weighted_average_price, self).create(cr, uid, vals, context)

weighted_average_price()
